import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

# Valida se o token foi carregado
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN não encontrado no arquivo .env")

notion = Client(auth=NOTION_TOKEN)
