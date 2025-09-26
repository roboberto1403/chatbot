from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Pega o URI do .env
uri = os.getenv("MONGO_URI")

# Cria cliente e conecta
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.chat_db
collection = db["chat_data"]
