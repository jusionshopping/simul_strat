import streamlit as st
import requests
from datetime import datetime, timedelta

# Introduce tu clave API de OpenWeather aquí
API_KEY = '04f994811920b474be6a629c1eb3a357'

# Función para obtener los datos del clima
def obtener_clima(lat, lon, fecha, hora):
    # Convertir la fecha y la hora seleccionada en un timestamp
    fecha_hora = datetime.combine(fecha, hora)
    timestamp = int(fecha_hora.timestamp())
    
    url = f"http://api.openweathermap.org/data/2.5/onecall/timemachine"
    params = {
        'lat': lat,
        'lon': lon,
        'dt': timestamp,  # Usamos el timestamp de la fecha y hora seleccionada
        'appid': API_KEY,
        'units': 'metric'  # Para obtener la temperatura en grados Celsius
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("No se pudo obtener la información del clima. Intenta nuevamente.")
        return None

# Mapa de circuitos con sus coordenadas
circuitos = {
    "Circuito de Spa-Francorchamps": {"lat": 50.4375, "lon": 5.9722},
    "Circuito de Monza": {"lat": 45.6150, "lon": 9.2811},
    "Circuito de Silverstone": {"lat": 52.0784, "lon": -1.0156},
    "Circuito de Barcelona-Cataluña": {"lat": 41.57, "lon": 2.2617}
}

# Interfaz en Streamlit
st.title("🌤️ Clima de Circuitos de F1")

# Seleccionar circuito
circuito = st.selectbox("Selecciona el circuito", list(circuitos.keys()))

# Seleccionar fecha
fecha = st.date_input("Selecciona la fecha", min_value=datetime.today())

# Seleccionar hora (hora de la pista, en formato de 24h)
hora = st.time_input("Selecciona la hora", value=datetime.now().time())

# Obtener los datos del clima al hacer clic en el botón
if st.button("Ver clima"):
    # Obtener las coordenadas del circuito seleccionado
    lat = circuitos[circuito]["lat"]
    lon = circuitos[circuito]["lon"]

    # Obtener el clima de esa fecha y hora
    clima = obtener_clima(lat, lon, fecha, hora)

    if clima:
        # Extraer solo los datos de la temperatura y lluvia
        temperatura = clima['current']['temp']  # Temperatura en °C
        lluvia = clima['current'].get('rain', {}).get('1h', 0)  # Lluvia en mm en la última hora

        # Mostrar la información del clima
        st.subheader(f"Clima para {circuito} el {fecha.strftime('%d-%m-%Y')} a las {hora.strftime('%H:%M')}")
        st.write(f"**Temperatura**: {temperatura} °C")
        st.write(f"**Precipitación (lluvia)**: {lluvia} mm")
