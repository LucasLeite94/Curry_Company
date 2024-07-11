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
import numpy as np

st.set_page_config(page_title='Visao Restaurantes', page_icon='#', layout='wide')

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

#=====================================================

def distance(df1):

    colums = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['Distance'] = df1.loc[:, colums].apply(lambda x:haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    avg_distance = np.round(df1 ['Distance'].mean(), (2))

    return avg_distance

#======================================================

def avg_std_time(df1, festival, op):

    cols = ['Time_taken(min)', 'Festival']
    df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    linhas_selecionadas = df_aux['Festival'] == festival
    df_aux = np.round(df_aux.loc[linhas_selecionadas, op], (2))

    return df_aux

#=======================================================

def avg_std_time_graph(df1):
    
    cols = ['Time_taken(min)', 'City']              
    df_aux = df1.loc[:, cols].groupby('City').agg( {'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict( type='data', array=df_aux['std_time'])))

    fig.update_layout(barmode='group')

    return fig

#=========================================================

def avg_std_city(df1):

    cols = ['City', 'Type_of_order', 'Time_taken(min)']  
    df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    return df_aux

#==========================================================

def graph_pie(df1):

    colums = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['Distance'] = df1.loc[:, colums].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

    avg = df1.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()

    fig = go.Figure( data=[go.Pie( labels=avg['City'], values=avg['Distance'], pull=[0, 0.1, 0])])

    return fig

#===========================================================

def graph_sun(df1):

    cols = ['Time_taken(min)', 'Road_traffic_density', 'City']
    df_aux = (df1.loc[:, cols].groupby(['City', 'Road_traffic_density'])
                .agg( {'Time_taken(min)': ['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], 
                                values='avg_time', color='std_time', 
                                color_continuous_scale='RdBu', 
                                color_continuous_midpoint=np.average
                                (df_aux['std_time']))
    
    return fig

#============================================================


            

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

st.header('Marketplace - Visão Restaurantes') # < Título > 

tab1, tab2, tab3 = st.tabs(['Crescimento Restaurantes', '_', '_'])

with tab1:
    
    # Criando container
    with st.container():

        # Crinado as colunas 
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        # Selecionando a coluna 1
        with col1:
            entrega_unico = len( df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('###### Entregadores únicos', entrega_unico)

        with col2:
            avg_distance = distance(df1)
            col2.metric('###### Distancia média das entregas', avg_distance)

        with col3:
            df_aux = avg_std_time(df1, 'Yes', 'avg_time')
            col3.metric( '###### Tempo médio de entrega com festival', df_aux)       

        with col4:
            df_aux = avg_std_time(df1, 'Yes', 'std_time')
            col4.metric( '###### O desvio padrão com festival', df_aux)


        with col5:
            df_aux = avg_std_time(df1, 'No', 'avg_time')
            col5.metric( '###### Tempo médio de entrega sem festival', df_aux)


        with col6:
            df_aux = avg_std_time(df1, 'No', 'std_time')
            col6.metric( '###### O desvio padrão sem festival', df_aux)
            

        st.markdown("""___""")

    # Criando container
    with st.container():
            
            # Criando colunas
        col1, col2 = st.columns(2)

        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)

        with col2:                      
            df_aux = avg_std_city(df1)
            st.dataframe(df_aux)


    st.markdown("""___""")

    # Criando container
    with st.container():

        #criando colunas 
        col1, col2 = st.columns(2)

        with col1:          
            fig = graph_pie(df1)
            st.plotly_chart(fig)

        with col2:
            fig = graph_sun(df1)
            st.plotly_chart(fig)

   

   

