import streamlit as st
import plotly.graph_objects as go

st.title("✏️ Diseñador de Estrategia")

# Entrada de parámetros generales
st.header("Parámetros generales")
tiempos = {}
degradaciones = {}

compuestos = ["SS", "S", "M", "H"]
for c in compuestos:
    tiempos[c] = st.number_input(f"Tiempo por vuelta con {c}", min_value=50.0, max_value=200.0, step=0.1)
    degradaciones[c] = st.number_input(f"Degradación por vuelta con {c} (%)", min_value=0, max_value=100, step=1)

tiempo_boxes = st.number_input("Tiempo de parada en boxes (s)", min_value=0.0, step=0.1)
vueltas_totales = st.number_input("Número total de vueltas de carrera", min_value=1, step=1)

# Penalización por degradación alta
st.header("Ajuste de penalización")
penalizacion_max = st.slider("Penalización máxima cuando la vida del neumático < 50%", 1.0, 2.0, 1.5, 0.1)

# Entrada de stints
st.header("Definición de estrategia (hasta 5 stints)")

stints = []
for i in range(5):
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
    vidas_por_stint = []  # [(stint_index, vuelta_global, vida)]
    for i, (tipo, vueltas) in enumerate(stints):
        if vueltas_acumuladas + vueltas > vueltas_totales:
            st.error(f"Te has pasado de vueltas en el stint {i+1}. Máximo permitido: {vueltas_totales - vueltas_acumuladas}")
            break

        tiempo_base = tiempos[tipo]
        degradacion = degradaciones[tipo] / 100
        vida_neumatico = 100
        tiempo_stint = 0
        
    if vidas_por_stint:
        st.subheader("📈 Vida del neumático por vuelta")
    
        fig = go.Figure()
    
        # Agrupar por stint
        for stint_num in set(s[0] for s in vidas_por_stint):
            vueltas = [v for s, v, vida in vidas_por_stint if s == stint_num]
            vidas = [vida for s, v, vida in vidas_por_stint if s == stint_num]
            fig.add_trace(go.Scatter(x=vueltas, y=vidas, mode='lines+markers', name=f'Stint {stint_num}'))
    
        fig.update_layout(
            xaxis_title='Vuelta',
            yaxis_title='Vida del neumático (%)',
            yaxis_range=[0, 100],
            template='plotly_dark'
        )
    
        st.plotly_chart(fig, use_container_width=True)


        for v in range(vueltas):
            if vida_neumatico < 50:
                penalizacion = 1 + ((0.5 - vida_neumatico / 100) * (penalizacion_max - 1) / 0.5)
            else:
                penalizacion = 1.0

            tiempo_vuelta = tiempo_base * penalizacion
            tiempo_stint += tiempo_vuelta

            vida_neumatico -= vida_neumatico * degradacion
            vida_neumatico = max(vida_neumatico, 0)

            vuelta_global = vueltas_acumuladas + v + 1  # Contador global de vueltas
            vidas_por_stint.append((i + 1, vuelta_global, vida_neumatico))

        total_tiempo += tiempo_stint
        if i > 0:
            total_tiempo += tiempo_boxes

        vueltas_acumuladas += vueltas

        st.markdown(f"**Stint {i+1}: {tipo} - {vueltas} vueltas**")
        st.write(f"🕒 Tiempo del stint: {tiempo_stint:.2f} s")
        st.write(f"🔋 Vida restante del neumático: {vida_neumatico:.1f} %")

    if vueltas_acumuladas < vueltas_totales:
        st.warning(f"Aún faltan {vueltas_totales - vueltas_acumuladas} vueltas por asignar.")
    elif vueltas_acumuladas > vueltas_totales:
        st.error(f"Te has pasado del total de vueltas permitido.")
    else:
        st.success(f"✅ Tiempo total de carrera (con paradas): {total_tiempo:.2f} s")
