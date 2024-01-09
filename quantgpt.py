import logging
import os
from typing import Optional
import openai
import chainlit as cl
from dotenv import load_dotenv

from llama_index.query_engine import RetrieverQueryEngine
from quantgptlib.simple_vector_storage import QuantSimpleVectorStorage

# Load environment variables
load_dotenv()

# obtain gpt model name from environment variables
gpt_model = os.getenv('GPT_MODEL')
gpt_temperature = float(os.getenv('GPT_TEMPERATURE'))

persist_dir = "./index"
source_folder = "./quant_scraper/docs"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

### Setup Storage
quant_storage = QuantSimpleVectorStorage(
    persist_dir="./index",
    gpt_model=gpt_model,
    gpt_temperature=gpt_temperature,
    source_folder=source_folder,
)

### Chat Callbacks
@cl.on_chat_start
async def on_chat_start():
    """
    This function is called when a chat session starts. It creates a query engine and sets it in the user session.
    It also greets the user with a message.
    """
    query_engine = quant_storage.create_query_engine(callback_handler=cl.LlamaIndexCallbackHandler())

    cl.user_session.set("query_engine", query_engine)

    app_user = cl.user_session.get("user")  # User class instead of AppUser
    await cl.Message(f"Hello {app_user.identifier}. How are you doing?").send()  # Updated to 'identifier'

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:  # Updated to User
    """
    Authenticates a user based on their username and password.
    """
    if (username, password) == ("admin", "admin"):
        return cl.User(identifier="admin", metadata={"role": "ADMIN"})  # Updated fields
    else:
        return None

@cl.on_message
async def main(message: cl.Message):
    """
    This function handles incoming messages.
    """
    query_engine = cl.user_session.get("query_engine")
    response = await cl.make_async(query_engine.query)(message.content)

    # Using cl.Step for intermediary steps (if applicable in your case)
    step = cl.Step()  # You might need to adjust this depending on your specific use case

    if hasattr(response, "response"):
        step.output = response.response  # Updated to use 'output' for Step

    await step.send()  # Updated to send Step instead of Message