#=============================
# Importando as bibliotecas
# ============================

from haversine import haversine  # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go  # type: ignore
import streamlit as st # type: ignore
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import pandas as pd

st.set_page_config(page_title='Visao Cliente', page_icon='#', layout='wide')

#==============================
# FUNÇÕES
#==============================
#   LIMPANDO O CÓDIGO
#   1- LIMPANDO OS NAN
#   2- CONVERTENDO AS COLUNAS 
#   3- REMOVENDO OS ESPAÇOS
#   4- LIMPANDO A COLUNA TIME_TAKEN

def clean_code ( df1 ):
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]

#=================================================================

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

#=======================================================
  
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

#====================================================
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

#====================================================

def graph_bar(df1):

    # Aplicando o grafico 
    cols = ['ID', 'Order_Date']

    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    fig = px.bar(df_aux, x='Order_Date', y='ID')
    
    return fig

#=====================================================

def graph_pie(df1):
    # Aplicando o gráfico
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    

    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

#=======================================================

def graph_scatter(df1):                 
    # Aplicando o gráfico
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()

    fig = px.scatter(df_aux, x='City', y= 'Road_traffic_density', size='ID', color='City')

    return fig

#=======================================================

def graph_line(df1):
    # Aplicando gráfico
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )

    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux.head()

    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

#========================================================

def graph_line1(df1):
    # Aplicando o gráfico
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how='inner')

    df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line( df_aux, x='week_of_year', y='Order_by_deliver' )

    return fig

#========================================================

def maps(df1):
    # Aplicando o grafico
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density',]).median().reset_index()#

    map = folium.Map()

    # Colocando os pontos do dateframe no mapa (Marker), (iterrows)<transforma em interação>

    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)

    # Exibindo o grafico de mapa dentro do streamlit (folium_static(map, Width= Heigth= < tamannho do mapa >))
    folium_static(map, width=1024, height=600)


#===============================
# Importando o dateframe
#===============================

df = pd.read_csv('train.csv')

df1 = df.copy()

df1 = clean_code(df)


#====================================
# Layout barra Lateral no streamlit
#====================================
# Incluir imagem
#image_path = '/home/lucas/Repos/logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

# Incluir títulos e sub-títulos
st.sidebar.markdown ('# Cury Company')
st.sidebar.markdown ('## Fastest Delivery in Town')
st.sidebar.markdown ("""___""") # < Criar uma linha divisória >

st.sidebar.markdown( '## Selecione uma data limite')

# Incluir filtro de rolagem
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime(2022, 4, 13),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')

st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione um tipo de trânsito')

# Incluir filtro de escolha
traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito?', 
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

#=============================================
# Ativando os filtros
#=============================================
# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#======================================
# Layout pagina central no Streamlit
#======================================

st.header('Marketplace - Visão Cliente') # < Título > 

# Criar abas dentro da visão
tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

# Trabalhar dentro das abas
with tab1:

    # Criando container (divisões dentro do layout)
    with st.container():
        st.markdown('# Orders by Day')                 
        fig = graph_bar(df1)
        # Exibindo o grafico dentro do streamlit (st.plotly_chart(variavel, use_container_width=True))
        st.plotly_chart(fig, use_container_width=True)

    # Criando container (divisões dentro do layout)
    with st.container():

        # Criando colunas 
        col1, col2 = st.columns(2)

        # Selecionado as colunas criadas
        with col1:  
            st.header('Traffic Order Share')
            fig = graph_pie(df1)
            # Exibindo o grafico dentro do streamlit (st.plotly_chart(variavel, use_container_width=True))
            st.plotly_chart(fig, use_coitainer_width=True)

        # Selecionando as clunas criadas
        with col2:
            st.header('Traffic Order City')
            fig = graph_scatter(df1)
            # Exibindo o grafico dentro do streamlit (st.plotly_chart(variavel, use_container_width=True))
            st.plotly_chart(fig, use_coitainer_width=True)   

   
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = graph_line(df1)
        # Exibindo o grafico dentro do streamlit (st.plotly_chart(variavel, use_container_width=True))
        st.plotly_chart(fig, use_coitainer_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = graph_line1(df1)
        # Exibindo o grafico dentro do streamlit (st.plotly_chart(variavel, use_container_width=True))
        st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.markdown ('# Country Maps')
    maps(df1)

    
