import streamlit as st

st.title("Diseñador de Estrategia")

# Entrada de parámetros generales
st.header("Parámetros generales")
tiempos = {}
degradaciones = {}

compuestos = ["SS", "S", "M", "H"]
for c in compuestos:
    tiempos[c] = st.number_input(f"Tiempo por vuelta con {c}", min_value=50.0, max_value=200.0, step=0.1)
    degradaciones[c] = st.number_input(f"Degradación por vuelta con {c} (%)", min_value=0, max_value=100, step=0)

tiempo_boxes = st.number_input("Tiempo de parada en boxes (s)", min_value=0.0, step=0.1)
vueltas_totales = st.number_input("Número total de vueltas de carrera", min_value=1, step=1)

# Entrada de stints
st.header("Definición de estrategia (hasta 6 stints)")

stints = []
for i in range(6):
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox(f"Neumático stint {i+1}", [""] + compuestos, key=f"tipo_{i}")
    with col2:
        vueltas = st.number_input(f"Vueltas stint {i+1}", min_value=0, max_value=vueltas_totales, step=1, key=f"vueltas_{i}")
    if tipo and vueltas > 0:
        stints.append((tipo, vueltas))

# Cálculos
if st.button("🚀 Calcular estrategia"):
    total_tiempo = 0
    vueltas_acumuladas = 0

    st.subheader("Resultados por stint")
    for i, (tipo, vueltas) in enumerate(stints):
        if vueltas_acumuladas + vueltas > vueltas_totales:
            st.error(f"Te has pasado de vueltas en el stint {i+1}. Máximo permitido: {vueltas_totales - vueltas_acumuladas}")
            break

        tiempo_vuelta_base = tiempos[tipo]
        degradacion = degradaciones[tipo] / 100

        vida_neumatico = 100
        tiempo_stint = 0

        for _ in range(vueltas):
            # Aplicar penalización solo si la vida del neumático está por debajo del 50%
            if vida_neumatico < 50:
                penalizacion = 1 + (0.5 - vida_neumatico / 100)  # escala de 1 a 1.5
                tiempo_vuelta = tiempo_vuelta_base * penalizacion
            else:
                tiempo_vuelta = tiempo_vuelta_base

            tiempo_stint += tiempo_vuelta
            vida_neumatico *= (1 - degradacion)

        total_tiempo += tiempo_stint
        if i > 0:
            total_tiempo += tiempo_boxes

        vueltas_acumuladas += vueltas

        st.markdown(f"**Stint {i+1}: {tipo} - {vueltas} vueltas**")
        st.write(f"🕒 Tiempo del stint: {tiempo_stint:.2f} s")
        st.write(f"🔋 Vida restante del neumático: {vida_neumatico:.2f} %")

    if vueltas_acumuladas < vueltas_totales:
        st.warning(f"Aún faltan {vueltas_totales - vueltas_acumuladas} vueltas por asignar.")
    elif vueltas_acumuladas > vueltas_totales:
        st.error(f"Te has pasado del total de vueltas permitido.")
    else:
        st.success(f"✅ Tiempo total de carrera (con paradas): {total_tiempo:.2f} s")
