import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


@st.fragment
def chart(df_banco_de_sangue: pd.DataFrame):
    """Retorna um gráfico de linha mostrando o histórico do estado do banco de 
        sangue por tipo sanguíneo"""

    try:
        # Conversão de tipo e renomeação de colunas para o gráfico
        df_banco_de_sangue['data_do_registro'] = pd.to_datetime(df_banco_de_sangue['data_do_registro'], format='mixed').dt.date
    except KeyError:
        return print('Dataframe vazio')

    df_banco_de_sangue.rename(columns={'tipo_sanguineo': 'Tipo Sanguíneo'}, inplace=True)
    estados_do_banco = {
        1: 'Crítico',
        2: 'Alerta',
        3: 'Reduzido',
        4: 'Estável',
        5: 'Adequado'
    }

    df_banco_de_sangue['estado_txt'] = df_banco_de_sangue['estado_do_estoque'].map(estados_do_banco)

    fig = px.line(
            df_banco_de_sangue,
            x='data_do_registro', 
            y='estado_do_estoque', 
            custom_data=['estado_txt', 'Tipo Sanguíneo'],
            color='Tipo Sanguíneo',
        )

    template_hover_estado_banco = '<b>%{customdata[1]}</b> %{customdata[0]}<extra></extra>'
    fig.update_traces(hovertemplate = template_hover_estado_banco)

    with st.container(border=True, horizontal=True):
        with st.container():
            st.plotly_chart(fig, width='stretch')

        with st.container(width=300, border=True):
            st.write('Legenda')
            st.caption(
                """
                <strong style='color:#ff0000;'>Nível 1 - Crítico</strong> Estoque baixíssimo, compromete os serviços que necessitam de sangue. Precisa urgentemente de doadores\n
                <b style='color:#FF6300;'>Nível 2 - Alerta</b> Estoque Baixo, porém não compromete os serviços que necessitam de sangue. Precisa de doadores\n
                <b style='color:#FFC300;'>Nível 3 - Reduzido</b> Estoque baixo, porém sem risco. É recomendável doar\n
                <b style='color:#6BFF2E;'>Nível 4 - Estável</b> Estoque abastecido. É recomendável seguir doando\n
                <b style='color:#0088FF;'>Nível 5 - Adequado</b> Estoque ideal, não há urgência para doações
                """,
                unsafe_allow_html=True
            )        



@st.fragment
def infos():
    with st.expander('Compatibilidade Sanguínea'):
        compatibilidade_sanguinea = {
            'A+': {'Recebe de': ['A+', 'A-', 'O+', 'O-'], 'Doa para': ['A+', 'AB+']},
            'A-': {'Recebe de': ['A-', 'O-'], 'Doa para': ['A+', 'A-', 'AB+', 'AB-']},
            'B+': {'Recebe de': ['B+', 'B-', 'O+', 'O-'], 'Doa para': ['B+', 'AB+']},
            'B-': {'Recebe de': ['B-', 'O-'], 'Doa para': ['B+', 'B-', 'AB+', 'AB-']},
            'AB+': {'Recebe de': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], 'Doa para': ['AB+']},
            'AB-': {'Recebe de': ['A-', 'B-', 'AB-', 'O-'], 'Doa para': ['AB+', 'AB-']},
            'O+': {'Recebe de': ['O+', 'O-'], 'Doa para': ['A+', 'B+', 'AB+', 'O+']},
            'O-': {'Recebe de': ['O-'], 'Doa para': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']}
        }

        tipo_selecionado = st.selectbox(
            label="Compatibilidade sanguínea", 
            options=list(compatibilidade_sanguinea.keys()),
            placeholder='Selecione o tipo sanguíneo',
            index=None
        )


        col1, col2 = st.columns(2)

        with col1:
            if tipo_selecionado is not None:
                recebe = ", ".join(compatibilidade_sanguinea[tipo_selecionado]['Recebe de'])
                st.success(f'**Recebe de:** {recebe}')

        with col2:
            if tipo_selecionado is not None:
                doa = ", ".join(compatibilidade_sanguinea[tipo_selecionado]['Doa para'])
                st.info(f'**Doa para:** {doa}')
            

        st.subheader('Visualização de compatibilidade sanguínea', text_alignment='center')

        tipos_sanguineos = [str(k) for k in compatibilidade_sanguinea.keys()]

        tab1, tab2 = st.tabs(["Rede de Doação (Hierárquica)", "Matriz de Compatibilidade"])

        # ==========================================
        # ABA 1: REDE HIERÁRQUICA (Plotly Graph Objects)
        # ==========================================
        with tab1:
            st.subheader("Rede Estruturada de Fluxo de Doação")

            # COORDENADAS AMPLIADAS: Espalhando melhor os pontos nos eixos X e Y
            # Negativos em X=1.0, Positivos em X=5.0 (Mais distantes na horizontal)
            # Níveis verticais de 2 em 2 unidades (Mais distantes na vertical)
            posicoes_nos = {
                'O-':  (1.0, 2.0), 'O+':  (5.0, 2.0),
                'B-':  (1.0, 4.0), 'B+':  (5.0, 4.0),
                'A-':  (1.0, 6.0), 'A+':  (5.0, 6.0),
                'AB-': (1.0, 8.0), 'AB+': (5.0, 8.0)
            }

            fig_rede = go.Figure()

            # Desenhando as setas direcionadas
            for doador in tipos_sanguineos:
                for receptor in tipos_sanguineos:
                    if (
                        doador != receptor
                        and receptor in compatibilidade_sanguinea[doador]["Doa para"]
                    ):
                        x0, y0 = posicoes_nos[doador]
                        x1, y1 = posicoes_nos[receptor]

                        dx, dy = x1 - x0, y1 - y0
                        dist = np.sqrt(dx**2 + dy**2)
                        
                        # Cria um desvio lateral suave para evitar linhas paralelas sobrepostas
                        desvia_lado = -0.35 if x0 == 5.0 else 0.35
                        ajuste_arco = desvia_lado * (abs(dy) * 0.12) if abs(dy) > 2 else 0

                        # Proporções de recuo ajustadas ao tamanho expandido da malha
                        recuo_origem = 0.45 / dist
                        recuo_destino = 0.5 / dist

                        x_start = x0 + dx * recuo_origem + ajuste_arco
                        y_start = y0 + dy * recuo_origem
                        x_end = x1 - dx * recuo_destino + ajuste_arco
                        y_end = y1 - dy * recuo_destino

                        # Configuração de cor sólida e sem opacidade conforme solicitado
                        cor_seta = "#198754" if doador == "O-" else "#dc3545"

                        fig_rede.add_annotation(
                            x=x_end,
                            y=y_end,
                            ax=x_start,
                            ay=y_start,
                            xref="x", yref="y",
                            axref="x", ayref="y",
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1.0,
                            arrowwidth=2.0,
                            arrowcolor=cor_seta,
                        )

            # Montagem dos nós baseada no posicionamento expandido
            x_nos = [posicoes_nos[tipo][0] for tipo in tipos_sanguineos]
            y_nos = [posicoes_nos[tipo][1] for tipo in tipos_sanguineos]

            cores_nos = []
            for tipo in tipos_sanguineos:
                if tipo == "O-": cores_nos.append("#198754")
                elif tipo == "AB+": cores_nos.append("#0d6efd")
                else: cores_nos.append("#dc3545")

            fig_rede.add_trace(
                go.Scatter(
                    x=x_nos,
                    y=y_nos,
                    mode="markers+text",
                    text=tipos_sanguineos,
                    textposition="middle center",
                    textfont=dict(color="white", size=13, weight="bold"),
                    marker=dict(size=44, color=cores_nos, line=dict(width=2, color="white")),
                    hovertemplate="Tipo Sanguíneo: %{text}<extra></extra>",
                )
            )

            fig_rede.update_layout(
                showlegend=False,
                margin=dict(b=20, l=40, r=40, t=20),
                # Limites dos eixos expandidos para enquadrar a nova escala de pontos
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.0, 6.0]),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[1.0, 9.0]),
                height=650,
                plot_bgcolor="rgba(0,0,0,0)",
            )

            st.plotly_chart(fig_rede, width='stretch')

        # ==========================================
        # ABA 2: MATRIZ DE COMPATIBILIDADE (Plotly Express)
        # ==========================================
        with tab2:
            st.subheader("Matriz de Doação e Recepção")
            
            dados_matriz = []
            for doador in tipos_sanguineos:
                linha = []
                for receptor in tipos_sanguineos:
                    if receptor in compatibilidade_sanguinea[doador]["Doa para"]:
                        linha.append(1)
                    else:
                        linha.append(0)
                dados_matriz.append(linha)

            df_matriz = pd.DataFrame(
                dados_matriz, index=tipos_sanguineos, columns=tipos_sanguineos
            )

            fig_heatmap = px.imshow(
                df_matriz,
                labels=dict(x="Quem Recebe", y="Quem Doa", color="Compatível"),
                x=tipos_sanguineos,
                y=tipos_sanguineos,
                color_continuous_scale=[[0, "#f8f9fa"], [1, "#dc3545"]],
            )

            fig_heatmap.update_traces(
                hoverongaps=False,
                hovertemplate="Doador: %{y}<br>Receptor: %{x}<br>Resultado: %{customdata}",
                customdata=np.where(df_matriz.values == 1, "Compatível ✔️", "Incompatível ❌"),
            )

            fig_heatmap.update_layout(
                coloraxis_showscale=False, width=600, height=500, xaxis_side="top"
            )

            st.plotly_chart(fig_heatmap, width='stretch')