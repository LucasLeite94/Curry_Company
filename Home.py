import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home', 
    page_icon='$$'
)

#image_path = '/home/lucas/Repos/logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

# Incluir títulos e sub-títulos
st.sidebar.markdown ('# Cury Company')
st.sidebar.markdown ('## Fastest Delivery in Town')
st.sidebar.markdown ("""___""") # < Criar uma linha divisória >

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
### Como utilizar esse Growth Dashboard?
- Visão Empresa:
    - Visão Gerencial: Métricas gerais  de comportamento.
    - Visão tática: Indicadores semanais de crescimento.
    - Visão Geográfica: Insights de geolocalização.
- Visão Entregador:
    - Acompanhamento dos indicadores semanais de crescimento.
- Visão Restaurante:
    - Indicadores semanais de crescimento dos restaurantes 
### Ask for Help
- Time de Data Science no Discord
    - @Lucas"""
)