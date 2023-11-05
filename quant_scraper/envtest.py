import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv("../.env"), override=True)

print(f"hello {os.getenv('VBT_PRO_SECRET_URL')}")