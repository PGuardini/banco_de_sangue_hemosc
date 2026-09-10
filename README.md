# Estado dos Bancos de Sangue HEMOSC
Este projeto tem como objetivo fazer a extração diária dos dados sobre o estado atual do estoque de sangue do banco de sangues do HEMOSC.

Os estados dos estoques do banco foram classificados conforme indicado abaixo:

|Índice| Estado | Descrição | Mensagem HEMOSC |
|------|--------|-----------|-----------------|
|1| Crítico | Estoque baixíssimo, podendo comprometer os serviços que necessitam de sangue. Precisa urgentemente de doadores | Precisamos de você! Convide seus familiares, amigos para virem também|
|2| Alerta | Estoque Baixo, porém não compromete os serviços que necessitam de sangue. Precisa de doadores| Venha doar e nos ajude a divulgar essa necessidade.|
|3| Reduzido | Estoque baixo, porém sem risco. É recomendável doar | Venha doar sangue, precisamos de você.|
|4| Estável | Estoque abastecido. É recomendável seguir doando| Continue doando para manter os estoques adequados.|
|5| Adequado | Estoque ideal, não há urgência para doações| O estoque está ideal. Continue nos acompanhando, e agende sua doação quando necessário.|

O banco de dados registra conforme o índice, o que facilita na hora de gerar o gráfico.
O gráfico é atualizado conforme o banco é atualizado. Todo dia há um novo registro no banco.

Todos os dados são extraídos da página <https://www.hemosc.org.br/>.