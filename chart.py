from sqlmodel import Session, select
import pandas as pd
import streamlit as st

from database import TipoSanguineo, RegistroEstoqueHemosc, engine

@st.fragment
def chart():
    """Retorna um gráfico de linha mostrando o histórico do estado do banco de 
        sangue por tipo sanguíneo"""

    with Session(engine) as s:
    # Query retorna Data do registro, Estado do estoque e Tipo sanguíneo
    # para ser transformado em dataframe
        statement = select(RegistroEstoqueHemosc.data_do_registro, 
                            RegistroEstoqueHemosc.estado_do_estoque, 
                            TipoSanguineo.tipo_sanguineo
                            ).join(TipoSanguineo)
        estados_do_estoque_atual = s.exec(statement)


    df_banco_de_sangue = pd.DataFrame(estados_do_estoque_atual)
    try:
        # Conversão de tipo e renomeação de colunas para o gráfico
        df_banco_de_sangue['data_do_registro'] = pd.to_datetime(df_banco_de_sangue['data_do_registro']).dt.date
    except KeyError:
        return print('Dataframe vazio')

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
@st.fragment
def infos():
    compatibilidade_sanguinea = {
        'A+': {
            'Recebe de': [
                'A+', 'A-', 'O+', 'O-'
            ],
            'Doa para': [
                'A+', 'AB+'
            ]
        },
        'A-': {
            'Recebe de': [
                'A-', 'O-'
            ],
            'Doa para': [
                'A+', 'A-', 'AB+', 'AB-'
            ]
        },
        'B+': {
            'Recebe de': [
                'B+', 'B-', 'O+', 'O-'
            ],
            'Doa para': [
                'B+', 'AB+'
            ]
        },
        'B-': {
            'Recebe de': [
                'B-', 'O-'
            ],
            'Doa para': [
                'B+', 'B-', 'AB+', 'AB-'
            ]
        },
        'AB+': {
            'Recebe de': [
                'A+', 'A-','B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
            ],
            'Doa para': [
                'AB+'
            ]
        },
        'AB-': {
            'Recebe de': [
                'A-', 'B-', 'AB-', 'O-'
            ],
            'Doa para': [
                'AB+', 'AB-'
            ]
        },
        'O+': {
            'Recebe de': [
                'O+', 'O-'
            ],
            'Doa para': [
                'A+', 'B+', 'AB+', 'O+'
            ]
        },
        'O-': {
            'Recebe de': [
                'O-'
            ],
            'Doa para': [
                'A+', 'A-','B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
            ]
        }
    }


    tipo_selecionado = st.selectbox(
        "Selecione o tipo sanguíneo:", 
        list(compatibilidade_sanguinea.keys())
    )

    col1, col2 = st.columns(2)

    with col1:
        recebe = ", ".join(compatibilidade_sanguinea[tipo_selecionado]['Recebe de'])

        st.success(f'**Recebe de:** {recebe}')

    with col2:
        doa = ", ".join(compatibilidade_sanguinea[tipo_selecionado]['Doa para'])
        st.info(f'**Doa para** {doa}')
        doa = ", ".join(compatibilidade_sanguinea[tipo_selecionado]['Doa para'])

    st.link_button('Agenda sua doação','https://www.hemosc.org.br/agende-sua-doacao.html')