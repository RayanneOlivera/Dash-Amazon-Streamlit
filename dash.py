import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Dashboard de Vendas - Amazon", layout="wide", initial_sidebar_state="expanded", page_icon="🛒")

@st.cache_data
def load_data():
    dados_vendas = pd.read_csv("Amazon Sale Report.csv", low_memory=False, dtype={'column_23': str})
    dados_clientes = pd.read_csv("online_retail.csv")
    return dados_vendas, dados_clientes

dados_vendas, dados_clientes = load_data()

st.sidebar.image("amazon_logo.png", width=100)

st.markdown("<h1 style='text-align: center; color: #FF9900; font-size: 36px;'>Dashboard de Vendas - Amazon</h1>", unsafe_allow_html=True)

pagina = st.sidebar.radio("Escolha a Análise", ["Vendas da Amazon", "Clientes"])

if pagina == "Vendas da Amazon":
    categorias = st.sidebar.multiselect("Selecione Categorias", options=dados_vendas["Category"].unique(), default=dados_vendas["Category"].unique())
    metodo_entrega = st.sidebar.selectbox("Selecione o Método de Entrega", options=dados_vendas["Fulfilment"].unique())
    
    dados_vendas_filtrados = dados_vendas[(dados_vendas["Category"].isin(categorias)) & (dados_vendas["Fulfilment"] == metodo_entrega)].copy()

    total_vendas = dados_vendas_filtrados["Amount"].sum()
    total_produtos = dados_vendas_filtrados["Qty"].sum()
    media_valor_venda = dados_vendas_filtrados["Amount"].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total de Vendas ($)", value=f"{total_vendas:,.2f}", delta_color="inverse")
    col2.metric(label="Total de Produtos Vendidos", value=total_produtos, delta_color="inverse")
    col3.metric(label="Média de Valor por Venda ($)", value=f"{media_valor_venda:,.2f}", delta_color="inverse")

    st.divider()

    col_grafico1, col_grafico2, col_grafico3 = st.columns(3)
    
    with col_grafico1:
        st.markdown("<h4 style='text-align: center; color: #FF9900;'>Distribuição de Quantidade Vendida por Categoria</h4>", unsafe_allow_html=True)
        fig_pizza = px.pie(dados_vendas_filtrados, names="Category", values="Qty", color_discrete_sequence=px.colors.sequential.Oranges)
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col_grafico2:
        st.markdown("<h4 style='text-align: center; color: #FF9900;'>Vendas por Método de Entrega</h4>", unsafe_allow_html=True)
        fig_barras = px.bar(dados_vendas_filtrados, x="Fulfilment", y="Amount", color="Fulfilment", text="Amount", color_discrete_sequence=px.colors.sequential.Oranges)
        fig_barras.update_layout(showlegend=False)
        st.plotly_chart(fig_barras, use_container_width=True)

    with col_grafico3:
        st.markdown("<h4 style='text-align: center; color: #FF9900;'>Tendência de Vendas ao Longo do Tempo</h4>", unsafe_allow_html=True)
        dados_vendas_filtrados["Date"] = pd.to_datetime(dados_vendas_filtrados["Date"])
        vendas_mensal = dados_vendas_filtrados.groupby(dados_vendas_filtrados["Date"].dt.to_period("M")).sum(numeric_only=True).reset_index()
        vendas_mensal["Date"] = vendas_mensal["Date"].dt.to_timestamp()
        fig_linha = px.line(vendas_mensal, x="Date", y="Amount", color_discrete_sequence=["#FF9900"])
        st.plotly_chart(fig_linha, use_container_width=True)

elif pagina == "Clientes":
    paises = st.sidebar.multiselect("Selecione Países", options=dados_clientes["Country"].unique(), default=dados_clientes["Country"].unique())

    dados_clientes_filtrados = dados_clientes[dados_clientes["Country"].isin(paises)].copy()
    
    total_clientes = dados_clientes_filtrados["CustomerID"].nunique()
    pais_mais_clientes = dados_clientes_filtrados["Country"].value_counts().idxmax()
    total_vendas_clientes = dados_clientes_filtrados["Quantity"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total de Clientes", value=total_clientes, delta_color="inverse")
    col2.metric(label="País com Mais Clientes", value=pais_mais_clientes, delta_color="inverse")
    col3.metric(label="Quantidade Total de Produtos Comprados", value=total_vendas_clientes, delta_color="inverse")

    st.divider()

    col_grafico1, col_grafico2 = st.columns(2)
    
    with col_grafico1:
        st.markdown("<h4 style='text-align: center; color: #FF9900;'>Clientes por País</h4>", unsafe_allow_html=True)
        fig_clientes_pais = px.bar(dados_clientes_filtrados["Country"].value_counts().reset_index(), x="index", y="Country", labels={"index": "País", "Country": "Número de Clientes"}, color_discrete_sequence=px.colors.sequential.Oranges)
        st.plotly_chart(fig_clientes_pais, use_container_width=True)

    with col_grafico2:
        st.markdown("<h4 style='text-align: center; color: #FF9900;'>Quantidade de Produtos Comprados por País e Categoria</h4>", unsafe_allow_html=True)
        dados_combinados = pd.merge(dados_vendas, dados_clientes, left_on="SKU", right_on="StockCode", how="inner")
        vendas_pais_categoria = dados_combinados.groupby(["Country", "Category"])["Qty"].sum().reset_index()
        vendas_pais_categoria = vendas_pais_categoria[vendas_pais_categoria["Country"].isin(paises)]
        fig_linhas = px.line(vendas_pais_categoria, x="Category", y="Qty", color="Country", color_discrete_sequence=px.colors.sequential.Oranges)
        st.plotly_chart(fig_linhas, use_container_width=True)

    st.markdown("<h4 style='text-align: center; color: #FF9900;'>Dispersão de Preço Unitário e Quantidade por País</h4>", unsafe_allow_html=True)
    fig_dispersao = px.scatter(dados_clientes_filtrados, x="UnitPrice", y="Quantity", color="Country", labels={"UnitPrice": "Preço Unitário", "Quantity": "Quantidade"}, color_discrete_sequence=px.colors.sequential.Oranges)
    st.plotly_chart(fig_dispersao, use_container_width=True)

st.markdown("<h3 style='color: #FF9900;'>Tabela Dinâmica</h3>", unsafe_allow_html=True)
st.dataframe(dados_vendas_filtrados if pagina == "Vendas da Amazon" else dados_clientes_filtrados, use_container_width=True)
