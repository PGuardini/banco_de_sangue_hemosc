# Bibliotecas Padrão
import os
import time
from datetime import datetime, date
from typing import List, Optional

# Bibliotecas para scraping
import requests
from bs4 import BeautifulSoup

# Biblioteca para manipulação de dados
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, func, select
import pandas as pd
import streamlit as st

class TipoSanguineo(SQLModel, table=True):
    __tablename__ = 'tipo_sanguineo'
    __table_args__ = {'extend_existing': True}

    id: int | None = Field(default=None, primary_key=True)
    tipo_sanguineo: str = Field(index=True)

    registros_estoque: List['RegistroEstoqueHemosc'] = Relationship(back_populates='tipo_sanguineo')

class RegistroEstoqueHemosc(SQLModel, table=True):
    __tablename__ = 'registro_estoque_hemosc'
    __table_args__ = {'extend_existing': True}

    id: int | None = Field(default=None, primary_key=True)
    data_do_registro: datetime = Field(default_factory = lambda: date.today())
    estado_do_estoque: int = Field(default=None, index=True)

    tipo_sanguineo_id: int | None = Field(default=None, foreign_key='tipo_sanguineo.id')

    tipo_sanguineo: Optional[TipoSanguineo] = Relationship(back_populates='registros_estoque')

engine = create_engine('sqlite:///hemosc.db', connect_args={'check_same_thread': False})

@st.cache_resource
def create_and_populate_db():
    print('Criando o banco de dados e tabelas')
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        total_tipos = session.exec(select(func.count(TipoSanguineo.id))).one()
        if total_tipos == 0:
            tipos_sanguineos = ['A-', 'A+', 'B-', 'B+', 'AB+', 'AB-', 'O+', 'O-']

            for tipo in tipos_sanguineos:
                novo_tipo = TipoSanguineo(tipo_sanguineo=tipo)
                session.add(novo_tipo)

            session.commit()



def crawler():
    """Abre a página do HEMOSC e grava os estoques de sangue atuais para cada
    tipo sanguíneo"""

    st.toast('Iniciando o crawler do HEMOSC...')    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    url = 'https://www.hemosc.org.br/'

    try:
        response = requests.get(url, headers=headers, timeout=60, verify=False)

    except Exception as e:
        st.error(f"Erro ao acessar o site do HEMOSC: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Retorna a div com o estado dos estoques de sangue
    div_estoque_de_sangue = soup.find_all('div', class_='dirt_home_estq')

    if not div_estoque_de_sangue:
        st.error("Não foi possível encontrar a div de estoques na página.")
        return


    st.toast('Extraindo o estado atual dos estoques de sangue')
    # Retorna a lista das divs de cada tipo sanguineo e seu estado de estoque
    estoque_diario_de_sangue_por_tipo = div_estoque_de_sangue[0].find_all('div')

    # Relação de estado de estoque da página com o estado do banco
    RELACAO_ESTADOS_DO_BANCO_DE_SANGUE = {
                            'Adequado':5,
                            'Estável':4,
                            'Reduzido':3,
                            'Alerta':2, 
                            'Crítico':1
                          }

    with Session(engine) as session:
        for estoque_por_tipo in estoque_diario_de_sangue_por_tipo:

            # Extrai o tipo sanguineo da tag img
            tipo_sanguineo = estoque_por_tipo.find('img').get('alt').split('tipo ')[-1]

            # Extrai o estoque atual do tipo sanguineo da tag img
            estoque_do_dia = estoque_por_tipo.find('img').get('title').split(' - ')[0]
            
            # Busca o tipo sanguineo no banco
            statement = select(TipoSanguineo.id).where(TipoSanguineo.tipo_sanguineo == tipo_sanguineo)
            grupo_tipo_sanguineo = session.exec(statement).first()

            # Busca identificador do estado do estoque no banco
            estado_do_estoque_hoje = RELACAO_ESTADOS_DO_BANCO_DE_SANGUE[estoque_do_dia]

            # Registra o novo estado no banco
            novo_registro = RegistroEstoqueHemosc(estado_do_estoque=estado_do_estoque_hoje,
                                                  tipo_sanguineo_id=grupo_tipo_sanguineo)

            session.add(novo_registro)
            #print(f'Gravando tipo {tipo_sanguineo} no banco')
            #print(f'Estoque atual do tipo {tipo_sanguineo}: {estoque_do_dia}')

        session.commit()

@st.fragment(run_every=60)
def timer():
    hoje = date.today()
    ultima_raspagem = None
    log = 'ultima_raspagem.txt'
    if os.path.exists(log):
        with open(log, 'r') as f:
            ultima_raspagem = date.fromisoformat(f.read())

    if hoje != ultima_raspagem:
        crawler()
        with open(log, 'w') as f:
            f.write(str(hoje))
    
    chart()

def chart():
    with Session(engine) as session:
        statement = select(RegistroEstoqueHemosc.data_do_registro, RegistroEstoqueHemosc.estado_do_estoque, TipoSanguineo.tipo_sanguineo).join(TipoSanguineo)

        df = pd.read_sql(statement, engine)
        df['data_do_registro'] = pd.to_datetime(df['data_do_registro']).dt.date
        df.rename(columns={'tipo_sanguineo': 'Tipo Sanguíneo'}, inplace=True)
        st.line_chart(df, 
                      x='data_do_registro', 
                      y='estado_do_estoque', 
                      color='Tipo Sanguíneo',
                      x_label='Dia',
                      y_label='Estado do Estoque',
                    )

def main():
    create_and_populate_db()
    timer()

if __name__ == "__main__":
    main()