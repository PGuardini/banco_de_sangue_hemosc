from sqlmodel import select
import pandas as pd
import streamlit as st

from database import TipoSanguineo, RegistroEstoqueHemosc, engine

def chart():
    """Retorna um gráfico de linha mostrando o histórico do estado do banco de 
        sangue por tipo sanguíneo"""

    # Query retorna Data do registro, Estado do estoque e Tipo sanguíneo
    # para ser transformado em dataframe
    statement = select(RegistroEstoqueHemosc.data_do_registro, 
                        RegistroEstoqueHemosc.estado_do_estoque, 
                        TipoSanguineo.tipo_sanguineo
                        ).join(TipoSanguineo)

    df_banco_de_sangue = pd.read_sql(statement, engine)

    # Conversão de tipo e renomeação de colunas para o gráfico
    df_banco_de_sangue['data_do_registro'] = pd.to_datetime(df_banco_de_sangue['data_do_registro']).dt.date
    df_banco_de_sangue.rename(columns={'tipo_sanguineo': 'Tipo Sanguíneo'}, inplace=True)

    # Plotagem do gráfico    
    st.line_chart(
                    df_banco_de_sangue, 
                    x='data_do_registro', 
                    y='estado_do_estoque', 
                    color='Tipo Sanguíneo',
                    x_label='Dia',
                    y_label='Estado do Estoque',
                )