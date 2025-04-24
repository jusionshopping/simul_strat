import streamlit as st
import itertools

st.set_page_config(page_title="Simulación de Estrategias", layout="centered")
st.title("🛞 Simulación de Estrategias")

# Valores predeterminados
def_val_neumaticos = ['SS', 'S', 'M', 'H']
def_val_duracion = [4, 7, 8, 11]
def_val_tiempos = [100.5, 101.6, 102.4, 103.5]

with st.form("parametros"):
    st.subheader("Parámetros de los Neumáticos")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        neumatico1 = st.text_input("Neumático 1", value=def_val_neumaticos[0])
        duracion1 = st.number_input("Duración 1", value=def_val_duracion[0], step=1)
        tiempo1 = st.number_input("Tiempo 1", value=def_val_tiempos[0], format="%0.2f")
    with col2:
        neumatico2 = st.text_input("Neumático 2", value=def_val_neumaticos[1])
        duracion2 = st.number_input("Duración 2", value=def_val_duracion[1], step=1)
        tiempo2 = st.number_input("Tiempo 2", value=def_val_tiempos[1], format="%0.2f")
    with col3:
        neumatico3 = st.text_input("Neumático 3", value=def_val_neumaticos[2])
        duracion3 = st.number_input("Duración 3", value=def_val_duracion[2], step=1)
        tiempo3 = st.number_input("Tiempo 3", value=def_val_tiempos[2], format="%0.2f")
    with col4:
        neumatico4 = st.text_input("Neumático 4", value=def_val_neumaticos[3])
        duracion4 = st.number_input("Duración 4", value=def_val_duracion[3], step=1)
        tiempo4 = st.number_input("Tiempo 4", value=def_val_tiempos[3], format="%0.2f")

    tiempo_boxes = st.number_input("⏱️ Tiempo parada en boxes (s)", min_value=0, value=20, step=1)
    duracion_carrera = st.number_input("🏁 Duración total de carrera (vueltas)", min_value=1, value=25, step=1)

    submitted = st.form_submit_button("🚀 Ejecutar Simulación")

if submitted:
    try:
        neumaticos = [neumatico1, neumatico2, neumatico3, neumatico4]
        duraciones = [duracion1, duracion2, duracion3, duracion4]
        tiempos = [tiempo1, tiempo2, tiempo3, tiempo4]

        duracion_neumaticos = dict(zip(neumaticos, duraciones))
        tiempos_vuelta = dict(zip(neumaticos, tiempos))

        combinaciones_temporales = []

        for num_stints in range(2, 5):
            combinaciones = list(itertools.product(neumaticos, repeat=num_stints))
            for combinacion in combinaciones:
                if len(set(combinacion)) >= 2:
                    stints = []
                    vueltas_totales = 0
                    for neumatico in combinacion:
                        duracion = duracion_neumaticos[neumatico]
                        stints.append((neumatico, duracion))
                        vueltas_totales += duracion
                    if vueltas_totales >= duracion_carrera:
                        tiempo_total = 0
                        vuelta_actual = 0
                        for neumatico, duracion in stints:
                            for _ in range(duracion):
                                tiempo_total += tiempos_vuelta[neumatico]
                                vuelta_actual += 1
                                if vuelta_actual >= duracion_carrera:
                                    break
                            if vuelta_actual < duracion_carrera:
                                tiempo_total += tiempo_boxes
                        combinaciones_temporales.append((tuple(stints), tiempo_total))

        dict_mejores = {}
        for stints, tiempo in combinaciones_temporales:
            clave = tuple(sorted(stints))
            if clave not in dict_mejores or tiempo < dict_mejores[clave][1]:
                dict_mejores[clave] = (stints, tiempo)

        mejores_resultados = sorted(dict_mejores.values(), key=lambda x: x[1])[:10]

        st.success("✅ Estrategias calculadas correctamente")
        for i, (estrategia, tiempo_total) in enumerate(mejores_resultados, 1):
            st.markdown(f"**Estrategia {i}:**")
            vuelta_actual = 0
            for j, (neumatico, duracion) in enumerate(estrategia, 1):
                vuelta_final = min(vuelta_actual + duracion, duracion_carrera)
                st.write(f"• Stint {j}: Neumático `{neumatico}`, Parada tras la vuelta **{vuelta_final}**")
                vuelta_actual = vuelta_final
            st.write(f"🕒 **Tiempo total de carrera:** `{tiempo_total:.2f} segundos`")
            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Error en la simulación: {e}")
