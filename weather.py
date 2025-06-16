import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import pandas as pd
import plotly.graph_objects as go

# Introduce tu clave API de OpenWeather aquí
API_KEY = '04f994811920b474be6a629c1eb3a357'

# Función para obtener los datos del clima

def obtener_clima(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("No se pudo obtener la información del clima. Intenta nuevamente.")
        return None

# Mapa de circuitos con sus coordenadas
circuitos = {
    "Australia (Melbourne)": {"lat": -37.8497, "lon": 144.9680},
    "Malasia (Sepang)": {"lat": 2.7608, "lon": 101.7382},
    "China (Shanghai)": {"lat": 31.3389, "lon": 121.2197},
    "Baréin (Sakhir)": {"lat": 26.0325, "lon": 50.5106},
    "España (Barcelona)": {"lat": 41.57, "lon": 2.2617},
    "Mónaco (Monte Carlo)": {"lat": 43.7347, "lon": 7.4206},
    "Turquía (Estambul)": {"lat": 40.9517, "lon": 29.4050},
    "Reino Unido (Silverstone)": {"lat": 52.0784, "lon": -1.0156},
    "Alemania (Hockenheim)": {"lat": 49.3278, "lon": 8.5658},
    "Hungría (Budapest)": {"lat": 47.5789, "lon": 19.2486},
    "Europa (Valencia)": {"lat": 39.4589, "lon": -0.3319},
    "Bélgica (Spa-Francorchamps)": {"lat": 50.4375, "lon": 5.9722},
    "Italia (Monza)": {"lat": 45.6150, "lon": 9.2811},
    "Singapur (Marina Bay)": {"lat": 1.2914, "lon": 103.8643},
    "Japón (Suzuka)": {"lat": 34.8431, "lon": 136.5419},
    "Brasil (Interlagos)": {"lat": -23.7036, "lon": -46.6997},
    "Abu Dabi (Yas Marina)": {"lat": 24.4672, "lon": 54.6031},
    "Francia (Paul Ricard)": {"lat": 43.2500, "lon": 5.7917},
    "Austria (Red Bull Ring)": {"lat": 47.2197, "lon": 14.7647},
    "Canadá (Montreal)": {"lat": 45.5000, "lon": -73.5228},
    "Azerbaiyán (Bakú)": {"lat": 40.3725, "lon": 49.8533},
    "México (Ciudad de México)": {"lat": 19.4042, "lon": -99.0907},
    "Rusia (Sochi)": {"lat": 43.4057, "lon": 39.9578},
    "Estados Unidos (Austin)": {"lat": 30.1328, "lon": -97.6411}
}

# Interfaz en Streamlit
st.title("🌤️ Clima de Circuitos de F1")

# Seleccionar circuito
circuito = st.selectbox("Selecciona el circuito", list(circuitos.keys()))

# Seleccionar fecha
fecha = st.date_input("Selecciona la fecha", value=datetime.today())

# Usar `session_state` para recordar la hora seleccionada
if "hora" not in st.session_state:
    st.session_state.hora = datetime.now().time()  # Valor por defecto: hora actual

# Hora seleccionada por el usuario
hora = st.time_input("Selecciona la hora", value=st.session_state.hora)

# Almacenar la hora seleccionada en `session_state`
if hora != st.session_state.hora:
    st.session_state.hora = hora

# Obtener los datos del clima al hacer clic en el botón
if st.button("Ver clima"):
    lat = circuitos[circuito]["lat"]
    lon = circuitos[circuito]["lon"]

    datos = obtener_clima(lat, lon)

    if datos:
        df = pd.DataFrame(datos['list'])
        if 'rain' not in df.columns:
            df['rain'] = [{}] * len(df)  # crea la columna rain con diccionarios vacíos
        df['fecha_hora'] = pd.to_datetime(df['dt'], unit='s', utc=True)
        df['temp'] = df['main'].apply(lambda x: x['temp'])
        df['lluvia'] = df['rain'].apply(lambda x: x.get('3h', 0) if isinstance(x, dict) else 0)
        df['lluvia'] = df['main'].apply(lambda x: 0)  # valor por defecto
        df['humedad'] = df['main'].apply(lambda x: x['humidity'])

        hora_carrera_utc = datetime.combine(fecha, hora).replace(tzinfo=timezone.utc)

        df_filtrado = df[df['fecha_hora'] <= hora_carrera_utc + timedelta(hours=3)]
        df_filtrado = df_filtrado[df_filtrado['fecha_hora'] >= hora_carrera_utc - timedelta(hours=10)]

        entrada_mas_cercana = df.iloc[(df['fecha_hora'] - hora_carrera_utc).abs().argsort().iloc[0]]

        temperatura = entrada_mas_cercana['temp']
        lluvia = entrada_mas_cercana['lluvia']
        humedad = entrada_mas_cercana['humedad']
        dt_forecast = entrada_mas_cercana['fecha_hora']
        inicio_franja = dt_forecast.strftime("%H:%M")
        fin_franja = (dt_forecast + timedelta(hours=3)).strftime("%H:%M")
        fecha_franja = dt_forecast.strftime("%d-%m-%Y")

        st.subheader(f"Clima estimado más cercano a {fecha.strftime('%d-%m-%Y')} {hora.strftime('%H:%M')} UTC")
        st.write(f"**Franja horaria de datos**: {fecha_franja} de {inicio_franja} a {fin_franja} UTC")
        st.write(f"**Temperatura**: {temperatura} °C")
        st.write(f"**Precipitación (últimas 3h)**: {lluvia} mm")
        st.write(f"**Humedad**: {humedad} %")


        # Gráfico con doble eje Y usando Plotly
        fig = go.Figure()

        # Temperatura (eje Y izquierdo)
        fig.add_trace(go.Scatter(x=df_filtrado['fecha_hora'], y=df_filtrado['temp'],
                                 mode='lines+markers', name='Temperatura (°C)',
                                 line=dict(color='orange'),
                                 yaxis='y1'))

        # Lluvia (eje Y derecho)
        fig.add_trace(go.Scatter(x=df_filtrado['fecha_hora'], y=df_filtrado['lluvia'],
                                 mode='lines+markers', name='Lluvia (mm)',
                                 fill='tozeroy', line=dict(color='blue'),
                                 yaxis='y2'))

        # Línea de hora de carrera
        fig.add_shape(type="line", x0=hora_carrera_utc, x1=hora_carrera_utc,
                      y0=0, y1=1, xref="x", yref="paper",
                      line=dict(color="red", width=2, dash="dash"))

        fig.add_annotation(x=hora_carrera_utc, y=1, xref="x", yref="paper",
                           text="Hora de carrera", showarrow=True, arrowhead=1, ax=0, ay=-40,
                           font=dict(color="red"))

        # Layout con doble eje Y
        fig.update_layout(
            title="📈 Evolución del clima (Temperatura y Lluvia)",
            xaxis=dict(title="Hora (UTC)"),
            yaxis=dict(title="Temperatura (°C)", tickfont=dict(color='orange')),
            yaxis2=dict(title="Lluvia (mm)", tickfont=dict(color='blue'),
                        overlaying='y', side='right'),
            hovermode="x unified",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)
    # Si la fecha es anterior a hoy, usar API histórica

    if fecha < datetime.today().date():
        st.info("Usando datos históricos (requiere suscripción de pago a OpenWeather)")
    
        fecha_hora_carrera = datetime.combine(fecha, hora)
        datos_historicos = obtener_clima_historico(lat, lon, fecha_hora_carrera)
    
        if datos_historicos:
            actual = datos_historicos['data'][0]  # Tomamos el dato más cercano
            temperatura = actual['temp']
            humedad = actual['humidity']
            lluvia = actual.get('rain', {}).get('1h', 0)  # Puede no estar presente
    
            st.subheader(f"🌤️ Clima histórico para {fecha.strftime('%d-%m-%Y')} a las {hora.strftime('%H:%M')}")
            st.write(f"**Temperatura**: {temperatura} °C")
            st.write(f"**Humedad**: {humedad} %")
            st.write(f"**Lluvia**: {lluvia} mm")

import time
def obtener_clima_historico(lat, lon, fecha_datetime):
    timestamp = int(time.mktime(fecha_datetime.timetuple()))
    
    url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
    params = {
        'lat': lat,
        'lon': lon,
        'dt': timestamp,
        'appid': API_KEY,
        'units': 'metric'
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("No se pudo obtener el clima histórico. Verifica tu suscripción y datos.")
        return None

