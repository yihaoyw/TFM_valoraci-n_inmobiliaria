"""Demo académica. Resultados y evaluación enlazados a los mismos artefactos."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import xgboost as xgb
from modelado import preparar

ROOT=Path(__file__).resolve().parent
ART=ROOT/'artefactos'
CITIES=('Madrid','Barcelona','Valencia')
st.set_page_config(page_title='VALORA | TFM',layout='wide')
st.title('VALORA · Motor de valoración inmobiliaria')
st.caption('Precio de oferta orientativo. Los modelos y sus errores se han evaluado con anuncios de 2018; no son una tasación ni una validación de precios actuales.')

@st.cache_resource
def load(city):
    meta=json.loads((ART/f'{city.lower()}_meta.json').read_text())
    models={q:xgb.XGBRegressor() for q in ('q10','q50','q90')}
    for q,m in models.items():m.load_model(str(ART/f'{city.lower()}_{q}.ubj'))
    return meta,models

@st.cache_data
def index():
    p=ROOT/'indice.json'
    return json.loads(p.read_text()) if p.exists() else None

city=st.selectbox('Ciudad',CITIES)
try:
    meta,models=load(city)
except FileNotFoundError:
    st.error('No hay modelos nuevos para esta ciudad. Ejecuta python entrenar.py y añade artefactos/.')
    st.stop()
idx=index()
district=st.selectbox('Distrito',sorted(meta['distritos']))
centroids=pd.DataFrame(meta['centroides'])
sub=centroids[centroids.distrito==district]
if len(sub)==0:
    st.error('No hay ubicación fiable para este distrito.')
    st.stop()
lat0,lon0=float(sub.lat.mean()),float(sub.lon.mean())
c1,c2,c3,c4=st.columns(4)
area=c1.number_input('Superficie construida (m²)',20,500,90)
rooms=c2.number_input('Habitaciones',0,15,3)
baths=c3.number_input('Baños',0,10,2)
year=c4.number_input('Año de construcción',1600,2018,1970)
c5,c6,c7,c8=st.columns(4)
lift=c5.checkbox('Ascensor',value=True)
terrace=c6.checkbox('Terraza')
parking=c7.checkbox('Garaje')
air=c8.checkbox('Aire acondicionado')
with st.expander('Ubicación aproximada y transporte'):
    st.caption('Por defecto se utiliza el centro de los barrios del distrito. Las coordenadas del portal mejoran la correspondencia con una vivienda concreta.')
    lat=st.number_input('Latitud',value=lat0,format='%.5f')
    lon=st.number_input('Longitud',value=lon0,format='%.5f')
    metro=st.number_input('Distancia a la estación de metro (km)',0.0,10.0,0.4)
    center=st.number_input('Distancia al centro (km)',0.0,30.0,float(meta['medianas_train'].get('DISTANCE_TO_CITY_CENTER',3)))

# Completar con medianas de TRAIN únicamente; la ausencia de esos atributos
# reduce precisión. No utilizar medias/valores del test ni del target.
d=dict(meta['medianas_train'])
d.update(CONSTRUCTEDAREA=area,ROOMNUMBER=rooms,BATHNUMBER=baths,
         CADCONSTRUCTIONYEAR=year,
         HASLIFT=int(lift),HASTERRACE=int(terrace),
         HASPARKINGSPACE=int(parking),HASAIRCONDITIONING=int(air),
         LATITUDE=lat,LONGITUDE=lon,DISTANCE_TO_METRO=metro,
         DISTANCE_TO_CITY_CENTER=center)
# Las derivadas se construyen con la misma función del entrenamiento.
x=preparar(pd.DataFrame([d]),meta['features'])
unit={q:float(np.exp(m.predict(x)[0])) for q,m in models.items()}
central=unit['q50']*area
adjustment=meta['ajuste_calibracion_eur']
low=max(0,min(unit['q10'],unit['q50'])*area-adjustment)
high=max(unit['q90'],unit['q50'])*area+adjustment
m=meta['evaluacion']
a,b=st.columns(2)
a.metric('Oferta estimada en euros de 2018',f'{central:,.0f} €')
b.metric('Intervalo calibrado para 2018',f'{low:,.0f} – {high:,.0f} €')
st.caption(f"Cobertura observada en test 2018: {m['cobertura_2018']:.1%}; error absoluto medio: {m['modelo']['mae_eur']:,.0f} €. Resultados sobre {m['n_test']:,} anuncios de test, separados por ASSETID.")
st.caption(f"Al simular los campos realmente disponibles en esta interfaz, el MAE fue {m['simulacion_campos_app']['mae_eur']:,.0f} € sobre ese mismo test. No supone cobertura validada para las predicciones hechas con campos omitidos.")

if idx and city in idx.get('ciudades',{}):
    current=idx['ciudades'][city]
    level=current.get(district)
    base=meta['distritos'][district]['media_2018_eur_m2']
    if not level:
        level=current['_ciudad']
        base=float(np.mean([z['media_2018_eur_m2'] for z in meta['distritos'].values()]))
        st.warning('No hay índice de distrito; se utiliza una aproximación de ciudad.')
    factor=float(level)/base
    with st.expander(f'Proyección orientativa con índice cargado ({idx["fecha"]})'):
        st.metric('Oferta reescalada',f'{central*factor:,.0f} €')
        st.write(f'Factor empleado: {factor:.3f}. Niveles externos del archivo indice.json; verificad fecha, definición y fuente antes de publicarlos.')
        st.warning('La cobertura del intervalo de 2018 y el MAE de 2018 NO han sido comprobados para esta proyección. No presentéis esta cifra como tasación actual validada.')

with st.expander('Evaluación, limitaciones y fuentes'):
    st.dataframe(pd.DataFrame([m[k]|{'metodo':k} for k in ('baseline_ciudad','baseline_distrito','modelo')]).set_index('metodo'))
    st.write('Validación espacial con distritos enteros nunca vistos:',m['espacial_distritos_nuevos'])
    st.write('Validación temporal de Q4 con viviendas nuevas:',m.get('temporal_q4_nuevos','no disponible'))
    st.write('El precio observado es de anuncio, no de compraventa. La app imputa características no solicitadas usando medianas de entrenamiento. Las viviendas reformadas o singulares y coordenadas aproximadas pueden generar errores grandes.')
    st.markdown('[Conjunto idealista18 y artículo](https://github.com/paezha/idealista18) · [Licencia ODbL](https://github.com/paezha/idealista18/blob/master/LICENSE.md)')

with st.expander('Ofertas de referencia de 2018 del conjunto de entrenamiento'):
    p=ART/f'{city.lower()}_comparables.json'
    if p.exists():
        comps=pd.DataFrame(json.loads(p.read_text()))
        st.caption('Muestra de anuncios, no ventas, seleccionada del entrenamiento; no equivale a inmuebles vendidos recientemente.')
        st.dataframe(comps[comps.DISTRITO==district].head(30),hide_index=True)
