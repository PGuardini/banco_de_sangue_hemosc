import streamlit as st

from chart import chart, infos
from data import get_worker_url, load_api_data

def main():
    st.set_page_config(page_title='HEMOSC Crawler', page_icon=':dna:', layout='wide')
    
    st.header('Estado do banco de sangue do HEMOSC', text_alignment='center')    
    
    WORKER_ESTOQUE_URL = get_worker_url()
    api_data = load_api_data(WORKER_ESTOQUE_URL)

    chart(api_data)
    infos()
    if st.sidebar.button('Atualizar dados agora'):
        load_api_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()