import streamlit as st

from chart import chart
from database import create_and_populate_db

def main():

    create_and_populate_db()

    st.title('Estado do banco de sangue do HEMOSC')

    chart()


if __name__ == "__main__":
    main()