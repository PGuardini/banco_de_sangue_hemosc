import streamlit as st

from chart import chart, infos
from data import get_worker_url, load_api_data

def main():
    st.set_page_config(page_title='HEMOSC Crawler', page_icon=':dna:', layout='wide')
    
    st.header('Estado do banco de sangue do HEMOSC', text_alignment='center')    
    
    WORKER_ESTOQUE_URL = get_worker_url()
    api_data = load_api_data(WORKER_ESTOQUE_URL)

    chart(api_data)
    st.space()
    with st.container(horizontal_alignment='center'):
        st.subheader('Faça da doação um hábito', text_alignment='center')
        st.markdown('''

                Apenas uma doação pode salvar até quatro vidas. Homens podem doar a cada 60 dias (até 4 vezes ao ano)
                 e mulheres a cada 90 dias (até 3 vezes ao ano).<br> 
                 Ao doar regularmente — e não apenas em campanhas ou 
                 situações de tragédia — você ajuda a manter a rede de saúde de Santa Catarina sempre preparada.
        ''', text_alignment='center', unsafe_allow_html=True)

        st.link_button('Agenda sua doação','https://www.hemosc.org.br/agende-sua-doacao.html', type='primary', )
    st.space()

    st.subheader('Informações sobre sangue', text_alignment='center')
    infos()


if __name__ == "__main__":
    main()