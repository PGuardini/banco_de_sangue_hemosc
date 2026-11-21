import streamlit as st

from chart import chart, infos
from data import get_worker_url, load_api_data

def main():
    st.title('Estado do banco de sangue do HEMOSC')
    WORKER_ESTOQUE_URL = get_worker_url()
    api_data = load_api_data(WORKER_ESTOQUE_URL)

    chart(api_data)
    infos()


if __name__ == "__main__":
    main()