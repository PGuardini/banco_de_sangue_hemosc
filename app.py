import streamlit as st

from chart import chart, infos
from database import create_and_populate_db, refresh_engine_if_needed

def main():
    refresh_engine_if_needed()
    create_and_populate_db()

    st.title('Estado do banco de sangue do HEMOSC')

    chart()
    infos()


if __name__ == "__main__":
    main()