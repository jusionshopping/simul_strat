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
    
    url = f"http://api.openweathermap.org/data/2.5/onecall"
    params = {
        'lat': lat,
        'lon': lon,
        'exclude': 'current,minutely,daily,alerts',  # Excluir datos no necesarios
        'appid': API_KEY,
        'units': 'metric',  # Para obtener la temperatura en grados Celsius
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("No se pudo obtener la información del clima. Intenta nuevamente.")
        return None

# Función para obtener la previsión futura (pronóstico por horas)
def obtener_prevision_futura(lat, lon, fecha, hora):
    # Convertir la fecha y la hora seleccionada en un timestamp
    fecha_hora = datetime.combine(fecha, hora)
    timestamp = int(fecha_hora.timestamp())

    url = f"http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'dt': timestamp
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
fecha = st.date_input("Selecciona la fecha", min_value=datetime.today())

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
    # Obtener las coordenadas del circuito seleccionado
    lat = circuitos[circuito]["lat"]
    lon = circuitos[circuito]["lon"]

    # Obtener los datos del clima para la hora seleccionada
    clima = obtener_prevision_futura(lat, lon, fecha, hora)

    if clima:
        # Extraer solo los datos de la temperatura y lluvia para esa hora
        from datetime import timezone
        
        # Hora deseada como timestamp UTC (la API trabaja en UTC)
        hora_deseada = int(datetime.combine(fecha, hora).replace(tzinfo=timezone.utc).timestamp())
        
        # Buscar la entrada más cercana en las próximas 5 días
        entrada_mas_cercana = min(clima['list'], key=lambda x: abs(x['dt'] - hora_deseada))
        
        temperatura = entrada_mas_cercana['main']['temp']
        lluvia = entrada_mas_cercana.get('rain', {}).get('3h', 0)  # porque es lluvia acumulada en 3 horas
        
        hora_forecast = datetime.utcfromtimestamp(entrada_mas_cercana['dt']).strftime("%d-%m-%Y %H:%M")
        
        dt_forecast = datetime.utcfromtimestamp(entrada_mas_cercana['dt'])
        inicio_franja = dt_forecast.strftime("%H:%M")
        fin_franja = (dt_forecast + timedelta(hours=3)).strftime("%H:%M")
        fecha_franja = dt_forecast.strftime("%d-%m-%Y")
        
        st.subheader(f"Clima estimado más cercano a {fecha.strftime('%d-%m-%Y')} {hora.strftime('%H:%M')} UTC")
        st.write(f"**Franja horaria de datos**: {fecha_franja} de {inicio_franja} a {fin_franja} UTC")
        st.write(f"**Temperatura**: {temperatura} °C")
        st.write(f"**Precipitación (últimas 3h)**: {lluvia} mm")


