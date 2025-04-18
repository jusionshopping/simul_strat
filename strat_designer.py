import streamlit as st
import plotly.graph_objects as go
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import io
from io import BytesIO

fecha_actual = date.today().strftime("%Y-%m-%d")
st.title("✏️ Diseñador de Estrategia")

# ----------------------------------------
# 📥 Cargar Excel previo
# ----------------------------------------
# Coloca la importación justo antes de los parámetros generales
archivo_subido = st.file_uploader("Importar estrategia (.xlsx)", type=["xlsx"])
datos_cargados = False

# Variables por defecto
tiempos = {}
degradaciones = {}
tiempos_personalizados = {}
degradaciones_personalizados = {}
compuestos = ["SS", "S", "M", "H"]
stints = []
tiempo_boxes_default = 0
vueltas_totales_default = 50
es_lluvia_default = False

# Si el archivo fue cargado correctamente
if archivo_subido:
    try:
        xls = pd.ExcelFile(archivo_subido)
        df_param = pd.read_excel(xls, sheet_name="Parámetros Generales")
        df_stint = pd.read_excel(xls, sheet_name="Estrategia")
        df_resumen = pd.read_excel(xls, sheet_name="Resumen")

        # Detectar lluvia
        lluvia_detectada = df_param["Compuesto"].str.contains("I|W").any()
        es_lluvia_default = lluvia_detectada

        # Cargar valores de "Resumen" (tiempo_boxes, vueltas_totales)
        for _, fila in df_resumen.iterrows():
            tiempo_boxes_default = fila["Tiempo en boxes (s)"]
            vueltas_totales_default = fila["Vueltas de carrera"]
            
        # Cargar tiempos y degradaciones de compuestos
        for _, fila in df_param.iterrows():
            compuesto = fila["Compuesto"]
            tiempo = fila["Tiempo por vuelta (s)"]
            degradacion = fila["Degradación (%)"]
            if compuesto in compuestos:
                tiempos[compuesto] = tiempo
                degradaciones[compuesto] = degradacion
            else:
                tiempos_personalizados[compuesto] = tiempo
                degradaciones_personalizados[compuesto] = degradacion

        # Cargar definición de estrategia
        for _, fila in df_stint.iterrows():
            stints.append((fila["Tipo"], int(fila["Vueltas"])))

        datos_cargados = True
        st.success("✅ Datos cargados correctamente.")
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {e}")


# ----------------------------------------
# Entrada de parámetros generales
# ----------------------------------------
st.header("Parámetros generales")

tiempo_boxes = st.number_input("Tiempo de parada en boxes (s)", min_value=0.0, step=0.1,
                               value=float(tiempo_boxes_default))
vueltas_totales = st.number_input("Vueltas de carrera", min_value=1, step=1,
                                  value=vueltas_totales_default)

es_lluvia = st.checkbox("¿Carrera en lluvia?", value=es_lluvia_default)

# Comp. estándar
for c in compuestos:
    tiempos[c] = st.number_input(f"Tiempo por vuelta con {c}", min_value=50.0, max_value=200.0, step=0.1,
                                 value=float(tiempos.get(c, 90.0)))  # Asegurarse de que sea float
    degradaciones[c] = st.number_input(f"Degradación por vuelta con {c} (%)", min_value=0, max_value=100, step=1,
                                       value=int(degradaciones.get(c, 5)))  # Si es entero, asegurarse de que sea int

# Si lluvia, mostrar campos extra
if es_lluvia:
    st.subheader("Neumáticos personalizados (Lluvia)")
    for c in ["I (Intermedios)", "W (Mojados)"]:
        tiempos_personalizados[c] = st.number_input(f"Tiempo por vuelta con {c}", min_value=50.0, max_value=200.0, step=0.1,
                                                    value=float(tiempos_personalizados.get(c, 100.0)))  # Asegurarse de que sea float
        degradaciones_personalizados[c] = st.number_input(f"Degradación por vuelta con {c} (%)", min_value=0, max_value=100, step=1,
                                                          value=int(degradaciones_personalizados.get(c, 7)))  # Asegurarse de que sea int

# ----------------------------------------
# Entrada de stints
# ----------------------------------------
st.header("Definición de estrategia (hasta 5 stints)")

nuevos_stints = []
for i in range(5):
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox(f"Neumático stint {i+1}", [""] + compuestos + (["I (Intermedios)", "W (Mojados)"] if es_lluvia else []),
                            key=f"tipo_{i}", index=([""] + compuestos + ["I (Intermedios)", "W (Mojados)"]).index(stints[i][0]) if i < len(stints) else 0)
    with col2:
        vueltas = st.number_input(f"Vueltas stint {i+1}", min_value=0, max_value=vueltas_totales, step=1,
                                  key=f"vueltas_{i}", value=stints[i][1] if i < len(stints) else 0)
    if tipo and vueltas > 0:
        nuevos_stints.append((tipo, vueltas))
stints = nuevos_stints

# ----------------------------------------
# Cálculos
# ----------------------------------------
if st.button("🚀 Calcular estrategia"):
    total_tiempo = 0
    vueltas_acumuladas = 0

    st.subheader("Resultados por stint")
    datos_grafico = []

    for i, (tipo, vueltas) in enumerate(stints):
        if vueltas_acumuladas + vueltas > vueltas_totales:
            st.error(f"Te has pasado de vueltas en el stint {i+1}. Máximo permitido: {vueltas_totales - vueltas_acumuladas}")
            break

        if tipo in tiempos:
            tiempo_vuelta_base = tiempos[tipo]
            degradacion = degradaciones[tipo] / 100
        else:
            tiempo_vuelta_base = tiempos_personalizados[tipo]
            degradacion = degradaciones_personalizados[tipo] / 100

        vida_neumatico = 100
        tiempo_stint = 0
        vidas_stint = []
        vueltas_stint = []

        for v in range(vueltas):
            if vida_neumatico < 50:
                penalizacion = 1 + (0.5 - vida_neumatico / 100)
                tiempo_vuelta = tiempo_vuelta_base * penalizacion
            else:
                tiempo_vuelta = tiempo_vuelta_base

            tiempo_stint += tiempo_vuelta
            vidas_stint.append(vida_neumatico)
            vueltas_stint.append(vueltas_acumuladas + v)
            vida_neumatico *= (1 - degradacion)

        vidas_stint.append(vida_neumatico)
        vueltas_stint.append(vueltas_acumuladas + vueltas)

        datos_grafico.append((tipo, vueltas_stint, vidas_stint))

        total_tiempo += tiempo_stint
        if i > 0:
            total_tiempo += tiempo_boxes

        vueltas_acumuladas += vueltas

        st.markdown(f"**Stint {i+1}: {tipo} - {vueltas} vueltas**")
        st.write(f"🕒 Tiempo del stint: {tiempo_stint:.2f} s")
        st.write(f"🔋 Vida restante del neumático: {vida_neumatico:.2f} %")

        if vueltas_acumuladas == vueltas_totales:
            st.success(f"✅ Tiempo total de carrera (con paradas): {total_tiempo:.2f} s")

# ----------------------------------------
# Gráfico
# ----------------------------------------
if 'datos_grafico' in locals() and datos_grafico:
    st.subheader("📉 Evolución de la vida del neumático")
    fig = go.Figure()
    vuelta_global = 0

    for i, (tipo, vueltas_stint, vidas_stint) in enumerate(datos_grafico):
        fig.add_trace(go.Scatter(x=vueltas_stint, y=vidas_stint, mode='lines+markers',
                                 name=f"Stint {i+1}: {tipo}"))
        vuelta_global = vueltas_stint[-1]

    fig.add_shape(type="line", x0=0, x1=vuelta_global, y0=50, y1=50,
                  line=dict(color="red", width=2, dash="dashdot"))

    fig.update_layout(
        xaxis_title="Vuelta",
        yaxis_title="Vida del neumático (%)",
        yaxis=dict(range=[0, 100]),
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    if vueltas_acumuladas < vueltas_totales:
        st.warning(f"Aún faltan {vueltas_totales - vueltas_acumuladas} vueltas por asignar.")
    elif vueltas_acumuladas > vueltas_totales:
        st.error(f"Te has pasado del total de vueltas permitido.")

# ----------------------------------------
# Exportar Excel e imagen
# ----------------------------------------
if stints:
    parametros = {
        'Compuesto': list(tiempos.keys()) + list(tiempos_personalizados.keys()),
        'Tiempo por vuelta (s)': list(tiempos.values()) + list(tiempos_personalizados.values()),
        'Degradación (%)': list(degradaciones.values()) + list(degradaciones_personalizados.values())
    }
    df_param = pd.DataFrame(parametros)

    estrategia = {
        'Stint': [f"Stint {i+1}" for i in range(len(stints))],
        'Tipo': [s[0] for s in stints],
        'Vueltas': [s[1] for s in stints]
    }
    df_stint = pd.DataFrame(estrategia)

    # Hoja resumen con tiempo de parada en boxes y vueltas totales
    resumen = {
        'Tiempo en boxes (s)': [tiempo_boxes],
        'Vueltas de carrera': [vueltas_totales]
    }
    df_resumen = pd.DataFrame(resumen)

    # Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_param.to_excel(writer, sheet_name='Parámetros Generales', index=False)
        df_stint.to_excel(writer, sheet_name='Estrategia', index=False)
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)  # Guardar la nueva hoja
    excel_buffer.seek(0)
    st.download_button("📥 Descargar datos en Excel", data=excel_buffer, file_name="estrategia_igp_{fecha_actual}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Imagen
    fig, axs = plt.subplots(2, 1, figsize=(10, 6))
    fig.tight_layout(pad=4)

    axs[0].axis('off')
    axs[0].set_title("Parámetros Generales", fontsize=12)
    tabla_param = axs[0].table(cellText=df_param.values, colLabels=df_param.columns, loc='center')
    tabla_param.auto_set_font_size(False)
    tabla_param.set_fontsize(10)

    axs[1].axis('off')
    axs[1].set_title("Definición de Estrategia", fontsize=12)
    tabla_stint = axs[1].table(cellText=df_stint.values, colLabels=df_stint.columns, loc='center')
    tabla_stint.auto_set_font_size(False)
    tabla_stint.set_fontsize(10)

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    st.download_button("🖼️ Exportar imagen", data=img_buffer, file_name=f"estrategia_igp_{fecha_actual}.png",
                       mime="image/png")
