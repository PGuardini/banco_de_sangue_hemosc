import os
from datetime import datetime, date
from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, func, select

### Models ###

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


### Setup do banco ###

caminho_do_banco = 'hemosc.db'

engine = create_engine(f'sqlite:///{caminho_do_banco}', connect_args={'check_same_thread': False})

def create_and_populate_db():
    print('Criando o banco de dados e tabelas')
    SQLModel.metadata.create_all(engine)

ultimo_tempo_de_modificacao = None

def refresh_engine_if_needed():
    global ultimo_tempo_de_modificacao

    try:
        tempo_de_modificacao_atual = os.path.getmtime(caminho_do_banco)
    except FileNotFoundError:
        return

    if tempo_de_modificacao_atual is not None and tempo_de_modificacao_atual != ultimo_tempo_de_modificacao:
        engine.dispose()

    ultimo_tempo_de_modificacao = tempo_de_modificacao_atual