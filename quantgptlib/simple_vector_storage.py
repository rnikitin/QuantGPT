import os
import logging
from typing import Iterator
from dotenv import load_dotenv
from llama_index import (
    LLMPredictor,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    get_response_synthesizer,
    ServiceContext,
)
from langchain.chat_models import ChatOpenAI
from llama_index.indices.postprocessor import SimilarityPostprocessor
from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.retrievers import VectorIndexRetriever
from llama_index.callbacks.base import CallbackManager
from llama_index.callbacks.base import BaseCallbackHandler
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import TokenTextSplitter

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuantSimpleVectorStorage:
    """
    A class that represents a simple vector storage for a GPT model.

    Attributes:
            persist_dir (str): The directory where the index and other data will be persisted.
            gpt_model (str): The name of the GPT model to use for predictions.
            gpt_temperature (float): The temperature to use for GPT predictions.
            source_folder (str): The folder containing the markdown files to use for indexing.
    """


class QuantSimpleVectorStorage:
    def __init__(self, persist_dir: str, gpt_model: str, gpt_temperature: float, source_folder: str):
        # collect arguments
        self.persist_dir = persist_dir
        self.gpt_model = gpt_model
        self.gpt_temperature = gpt_temperature
        self.source_folder = source_folder

        # initialize attributes
        self.index = None
        self.llm_predictor = self.create_llm_predictor()

        # setup index
        self.setup_index()

    def list_sources(self) -> Iterator[str]:
        """
        Returns an iterator over the paths of all markdown files in the source folder, excluding certain files.

        Excluded files:
        - api.md
        - all_pages.md
        - unknown.md
        - chainlit.md
        """
        exclude_files = {"api.md", "all_pages.md", "unknown.md", "chainlit.md"}
        for root, _, files in os.walk(self.source_folder):
            for file in files:
                if file.endswith(".md") and file not in exclude_files:
                    yield os.path.join(root, file)

    def create_llm_predictor(self) -> LLMPredictor:
        """
        Sets up and returns an instance of the LLMPredictor class, which uses the ChatOpenAI class
        to generate predictions based on the GPT model specified by the `gpt_model` attribute of this
        SimpleVectorStorage instance.

        Returns:
                An instance of the LLMPredictor class.
        """
        return LLMPredictor(
            llm=ChatOpenAI(
                temperature=self.gpt_temperature,
                model_name=self.gpt_model,
                max_tokens=2048,
                streaming=True,
            ),
        )

    def load_index_nodes(self):
        logger.info('Loading documents...')

        text_splitter = TokenTextSplitter(
            separator="## ", chunk_size=1024, chunk_overlap=128)

        node_parser = SimpleNodeParser.from_defaults(
            text_splitter=text_splitter,
        )

        documents = SimpleDirectoryReader(
            input_files=self.list_sources()).load_data()

        index_nodes = node_parser.get_nodes_from_documents(
            documents, show_progress=True)

        return index_nodes

    def create_index(self):
        logger.info('Building index...')

        index = VectorStoreIndex(
            nodes=self.load_index_nodes(),
            show_progress=True,
            service_context=ServiceContext.from_defaults(
                llm_predictor=self.llm_predictor,
            )
        )

        return index

    def setup_index(self):
        """
        Sets up the index for the vector store. If the index is already present in the storage context, it is loaded
        from there. Otherwise, a new index is built from the markdown files in the input directory and saved to the
        storage context for future use.
        """
        try:
            logger.info('Loading index...')
            storage_context = StorageContext.from_defaults(
                persist_dir=self.persist_dir)
            self.index = load_index_from_storage(storage_context)
        except Exception as e:
            logger.info('Persisted Index not found, building new one.')

            # create index
            self.index = self.create_index()

            logger.info('Saving index...')
            self.index.storage_context.persist(persist_dir=self.persist_dir)

    def create_service_context(self, callback_handler: BaseCallbackHandler = None) -> ServiceContext:
        """
        Creates a new ServiceContext instance with default settings.

        Returns:
                A new ServiceContext instance.
        """
        llm_predictor = self.create_llm_predictor()

        return ServiceContext.from_defaults(
            llm_predictor=llm_predictor,
            chunk_size=1024,
            callback_manager=CallbackManager([callback_handler])
        )

    def create_query_engine(self, callback_handler: BaseCallbackHandler = None) -> RetrieverQueryEngine:
        """
        Creates a RetrieverQueryEngine object with the configured VectorIndexRetriever and response synthesizer.

        Returns:
                RetrieverQueryEngine: The created RetrieverQueryEngine object.
        """

        service_context = self.create_service_context(callback_handler)

        # Configure retriever within the service context
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=10,
        )

        # Configure response synthesizer within the service context
        response_synthesizer = get_response_synthesizer(
            response_mode="tree_summarize", service_context=service_context)

        # Assemble query engine
        query_engine = RetrieverQueryEngine.from_args(
            streaming=True,
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            service_context=service_context,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=0.7)
            ]
        )
        return query_engine
