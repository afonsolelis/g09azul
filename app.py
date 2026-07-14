import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="Exemplo Streamlit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def gerar_dados_exemplo():
    np.random.seed(42)
    datas = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    dados = {
        'data': datas,
        'vendas': np.random.randint(100, 1000, len(datas)),
        'categoria': np.random.choice(['Eletrônicos', 'Roupas', 'Casa', 'Esportes'], len(datas)),
        'regiao': np.random.choice(['Norte', 'Sul', 'Leste', 'Oeste'], len(datas)),
        'cliente_novo': np.random.choice([True, False], len(datas), p=[0.3, 0.7])
    }
    return pd.DataFrame(dados)

def main():
    st.title("📊 Dashboard de Exemplo - Streamlit")
    st.markdown("---")
    
    df = gerar_dados_exemplo()
    
    with st.sidebar:
        st.header("🔧 Filtros")
        
        categorias = st.multiselect(
            "Categorias",
            options=df['categoria'].unique(),
            default=df['categoria'].unique()
        )
        
        regioes = st.multiselect(
            "Regiões",
            options=df['regiao'].unique(),
            default=df['regiao'].unique()
        )
        
        data_inicio = st.date_input(
            "Data Início",
            value=df['data'].min(),
            min_value=df['data'].min(),
            max_value=df['data'].max()
        )
        
        data_fim = st.date_input(
            "Data Fim",
            value=df['data'].max(),
            min_value=df['data'].min(),
            max_value=df['data'].max()
        )
        
        mostrar_raw = st.checkbox("Mostrar dados brutos", False)
    
    df_filtrado = df[
        (df['categoria'].isin(categorias)) &
        (df['regiao'].isin(regioes)) &
        (df['data'] >= pd.Timestamp(data_inicio)) &
        (df['data'] <= pd.Timestamp(data_fim))
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Vendas",
            f"R$ {df_filtrado['vendas'].sum():,.0f}",
            delta=f"{np.random.randint(-10, 10)}%"
        )
    
    with col2:
        st.metric(
            "Média Diária",
            f"R$ {df_filtrado['vendas'].mean():,.0f}",
            delta=f"{np.random.randint(-5, 5)}%"
        )
    
    with col3:
        st.metric(
            "Clientes Novos",
            f"{df_filtrado['cliente_novo'].sum():,}",
            delta=f"{np.random.randint(-3, 3)}%"
        )
    
    with col4:
        st.metric(
            "Dias no Período",
            f"{len(df_filtrado):,}",
        )
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Série Temporal", "📊 Por Categoria", "🗺️ Por Região", "📋 Dados"])
    
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            fig_linha = px.line(
                df_filtrado.groupby('data')['vendas'].sum().reset_index(),
                x='data', y='vendas',
                title='Vendas Diárias',
                labels={'data': 'Data', 'vendas': 'Vendas (R$)'}
            )
            fig_linha.update_layout(height=400)
            st.plotly_chart(fig_linha, use_container_width=True)
        
        with col_right:
            fig_area = px.area(
                df_filtrado.groupby('data')['vendas'].sum().reset_index(),
                x='data', y='vendas',
                title='Vendas Acumuladas'
            )
            fig_area.update_layout(height=400)
            st.plotly_chart(fig_area, use_container_width=True)
    
    with tab2:
        col_left, col_right = st.columns(2)
        
        with col_left:
            vendas_cat = df_filtrado.groupby('categoria')['vendas'].sum().reset_index()
            fig_bar = px.bar(
                vendas_cat, x='categoria', y='vendas',
                title='Vendas por Categoria',
                color='categoria',
                text_auto=True
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_right:
            fig_pie = px.pie(
                vendas_cat, values='vendas', names='categoria',
                title='Distribuição por Categoria'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        col_left, col_right = st.columns(2)
        
        with col_left:
            vendas_reg = df_filtrado.groupby('regiao')['vendas'].sum().reset_index()
            fig_bar_reg = px.bar(
                vendas_reg, x='regiao', y='vendas',
                title='Vendas por Região',
                color='regiao',
                text_auto=True
            )
            st.plotly_chart(fig_bar_reg, use_container_width=True)
        
        with col_right:
            vendas_cat_reg = df_filtrado.groupby(['regiao', 'categoria'])['vendas'].sum().reset_index()
            fig_heatmap = px.density_heatmap(
                vendas_cat_reg, x='regiao', y='categoria', z='vendas',
                title='Vendas: Região vs Categoria',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab4:
        if mostrar_raw:
            st.dataframe(df_filtrado, use_container_width=True, height=400)
        else:
            st.info("Marque 'Mostrar dados brutos' na barra lateral para ver a tabela completa")
            
            resumo = df_filtrado.groupby(['categoria', 'regiao']).agg({
                'vendas': ['sum', 'mean', 'count'],
                'cliente_novo': 'sum'
            }).round(2)
            resumo.columns = ['Total Vendas', 'Média Vendas', 'Qtd Registros', 'Clientes Novos']
            st.dataframe(resumo, use_container_width=True)
    
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            Exemplo Streamlit | Dados simulados para demonstração
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()