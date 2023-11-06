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

    app_user = cl.user_session.get("user")
    await cl.Message(f"Hello {app_user.username}. How are you doing?").send()


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.AppUser]:
    """
    Authenticates a user based on their username and password.

    Args:
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.

    Returns:
        Optional[cl.AppUser]: An instance of `cl.AppUser` if the user is authenticated, otherwise `None`.
    """
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.AppUser(username="admin", role="ADMIN", provider="credentials")
    else:
        return None


@cl.on_message
async def main(message: cl.Message):
    """
    This function takes a message object as input, queries a RetrieverQueryEngine object with the message content,
    and sends the response back to the user in a message object.
    """
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
