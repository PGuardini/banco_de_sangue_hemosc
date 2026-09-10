import logging
import requests
import sys

from bs4 import BeautifulSoup
from sqlmodel import Session, select

from database import engine, create_and_populate_db, RegistroEstoqueHemosc, TipoSanguineo

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def crawler():
    """Abre a página do HEMOSC e grava os estoques de sangue atuais para cada
    tipo sanguíneo"""

    logger.info('Iniciando o crawler do HEMOSC...')    

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    url = 'https://www.hemosc.org.br/'

    try:
        response = requests.get(url, headers=headers, timeout=60, verify=False)

    except Exception as e:
        logger.error(f"Erro ao acessar o site do HEMOSC: {e}")

        sys.exit(1)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Retorna a div com o estado dos estoques de sangue
    div_estoque_de_sangue = soup.find_all('div', class_='dirt_home_estq')

    if not div_estoque_de_sangue:
        logger.error("Não foi possível encontrar a div de estoques na página.")

        sys.exit(1)

    logger.info('Extraindo o estado atual dos estoques de sangue')
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

            logger.info(f'Gravando tipo {tipo_sanguineo} no banco')
            logger.info(f'Estoque atual do tipo {tipo_sanguineo}: {estoque_do_dia}')

        session.commit()

    logger.info('Raspagem concluída com sucesso!')

if __name__ == '__main__':
    create_and_populate_db()
    crawler()