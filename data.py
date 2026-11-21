import os
import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

def get_worker_url() -> str:
    """Retorna a url do worker que faz consulta no banco de dados"""
    try:
        if 'WORKER_ESTOQUE_URL' in st.secrets:
            return st.secrets['WORKER_ESTOQUE_URL']
    except:
        load_dotenv()
        url = os.getenv('WORKER_ESTOQUE_URL')
        return url


st.cache_data(ttl=1800, show_spinner='Buscando dados do banco de sangue do HEMOSC...')
def load_api_data(url: str) -> pd.DataFrame:
    resp = requests.get(url, timeout=20)
    data = resp.json()

    if not data:
        return pd.DataFrame(
                        columns=["id", "tipo_sanguineo", "data_do_registro", "estado_do_estoque"]
                )

    df = pd.DataFrame(data)

    return df