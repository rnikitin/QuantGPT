import logging
import os
from typing import Iterator, Optional
import openai

from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.callbacks.base import CallbackManager
from langchain.chat_models import ChatOpenAI
import chainlit as cl
from dotenv import load_dotenv

from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.indices.postprocessor import SimilarityPostprocessor
from llama_index.chat_engine.types import BaseChatEngine, ChatMode

from llama_index import (
    LLMPredictor,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
    set_global_service_context,
)
from llama_index import (
    VectorStoreIndex,
    get_response_synthesizer,
)

# Load environment variables
load_dotenv()

# obtain gpt model name from environment variables
gpt_model = os.getenv('GPT_MODEL')
gpt_temperature = float(os.getenv('GPT_TEMPERATURE'))

persist_dir = "./index"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


def list_markdown_files(directory: str) -> Iterator[str]:
    """List all markdown files from the specified directory and its subdirectories,
    ignoring certain files."""
    exclude_files = {"api.md", "all_pages.md", "unknown.md", "chainlit.md"}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md") and file not in exclude_files:
                yield os.path.join(root, file)


### Setup Index
try:
    logger.info('Loading index...')
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    # load index
    index = load_index_from_storage(storage_context)
except:
    logger.info('Index not found, building new one.')
    from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader

    logger.info('Loading documents...')
    documents = SimpleDirectoryReader(input_files=list(
        list_markdown_files("./quant_scraper/docs"))).load_data()
    logger.info('Building index...')
    index = GPTVectorStoreIndex.from_documents(documents, show_progress=True)
    logger.info('Saving index...')
    index.storage_context.persist(persist_dir=persist_dir)

### Chat Callbacks

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.AppUser]:
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.AppUser(username="admin", role="ADMIN", provider="credentials")
    else:
        return None


@cl.on_chat_start
async def on_chat_start():
    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(
            temperature=gpt_temperature,
            model_name=gpt_model,
            max_tokens=2048,
            streaming=True,
        ),
    )
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        chunk_size=1024,
        callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]),
    )

    set_global_service_context(service_context)

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=10,
    )
    # configure response synthesizer
    response_synthesizer = get_response_synthesizer(
        response_mode="tree_summarize", service_context=service_context)

    # assemble query engine
    query_engine = RetrieverQueryEngine.from_args(
        streaming=True,
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        service_context=service_context,
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.7)
        ]
    )

    cl.user_session.set("query_engine", query_engine)

    app_user = cl.user_session.get("user")
    await cl.Message(f"Hello {app_user.username}. How are you doing?").send()


@cl.on_message
async def main(message: cl.Message):
    query_engine = cl.user_session.get(
        "query_engine")  # type: RetrieverQueryEngine
    response = await cl.make_async(query_engine.query)(message.content)

    response_message = cl.Message(content="")

    if hasattr(response, "response_gen"):
        for token in response.response_gen:
            await response_message.stream_token(token=token)

    # response_message.content = response.

    if hasattr(response, "response"):
        response_message.content = response.response

    await response_message.send()
