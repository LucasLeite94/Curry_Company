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

st.set_page_config(page_title='Visao Entregadores', page_icon='#', layout='wide')

#===============================
# Funções
#===============================
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

    #===================================================================
  
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

#===========================================================

def top_delivers( df1, top_asc ):
       
    df2 = ( df1.loc[:, ['City', 'Time_taken(min)', 'Delivery_person_ID']]
               .groupby(['City', 'Delivery_person_ID'])
               .max()
               .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
               .reset_index() )
                    # Aplicando o código
    df2 = df1.loc[:, ['City', 'Time_taken(min)', 'Delivery_person_ID']].groupby(['City', 'Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending=False).reset_index()
    df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat( [df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
                    
    return df3


#===============================
# Importando o dateframe
#===============================

df = pd.read_csv('train.csv')

df1 = df.copy()

df1 = clean_code( df )


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

st.sidebar.markdown('## Selecione uma condição climática')

# Incluir filtro de escolha
conditions_options = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    ["conditions Sunny", "conditions Stormy", "conditions Sandstorms", "conditions Cloudy", "conditions Windy", "conditions Fog" ],
    default=["conditions Sunny", "conditions Stormy", "conditions Sandstorms", "conditions Cloudy", "conditions Windy", "conditions Fog" ])


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

# Filtro de condição climática
linhas_selecionadas = df1['Weatherconditions'].isin(conditions_options)
df1 = df1.loc[linhas_selecionadas, :]


#======================================
# Layout pagina central no Streamlit
#======================================

st.header('Marketplace - Visão Entregadores') # < Título > 

tab1, tab2, tab3 = st.tabs(['Crescimento Entregadores', '_', '_'])

with tab1:

    # Criando o 1° Container
    with st.container():

        # Título
        st.title('Overall metrics')

        # Criando as colunas 
        col1, col2, col3, col4 = st.columns(4)

        # Selecionando a col 1
        with col1:
            
            # Aplicando os códigos
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        # Selecionando a col 2
        with col2:
            
            # Aplicando os códigos
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)

        # Selecionando a col 3
        with col3:
            
            # Aplicando os códigos
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)


        # Selecionando a col 4
        with col4:
          
            # Aplicando os códigos
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
    
    # Criando o 2° Container
    with st.container():

         # Linha divisória
        st.markdown("""___""")

        # Título
        st.title('Avaliações')

        # Criando as colunas
        col1, col2 = st.columns(2)
        
        # Selecionando a col 1
        with col1:
            st.markdown('##### Avaliacões médias por entregador')

            # Aplicando o código
            avaliacao_media = df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            
            # Visualizando o dateframe
            st.dataframe(avaliacao_media)

        # Selecionando a col 2
        with col2:
            st.markdown('##### Avaliacões médias por tipo de trânsito')

            
            df_aux = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg( {'Delivery_person_Ratings' : ('mean', 'std')})
            df_aux.columns = ['Delivery_mean', 'Delivery_std']

            # Visualizando o dateframe
            st.dataframe((df_aux).reset_index())


            st.markdown('##### Avaliacões médias por condicões climáticas')

            # Aplicando o código
            df_aux = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg( {'Delivery_person_Ratings' : ('mean', 'std')})
            df_aux.columns = ['Delivery_mean', 'Delivery_std']

            # Visualizando o dateframe
            st.dataframe((df_aux).reset_index())

    # Criando o 3° Container
    with st.container():

        # Linha divisória
        st.markdown("""___""")
         
         # Título
        st.title('velocidade de entrega')

        # Criando as colunas
        col1, col2 = st.columns(2)

        # Selecionando a col 1
        with col1:
            st.markdown('##### Entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc= True)
            st.dataframe(df3)

        
        # Selecionando a col 2
        with col2:
            st.markdown('##### Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc= False)
            st.dataframe(df3)
            

            


        





