import streamlit as st
import itertools

def duracion_neum(degrad):
    vida_neum = 100.0
    vueltas = 0
    durac = []
    for porcentaje in degrad:
        while vida_neum > 50:
            vida_neum -= vida_neum * (porcentaje / 100)
            vueltas += 1
        durac.append(vueltas)
        vida_neum = 100.0
        vueltas = 0
    return durac

st.title("🛞 Simulación de Estrategias de Neumáticos")

st.subheader("Configuración de neumáticos")
neum = [st.text_input(f"Neumático {i+1}", value=n) for i, n in enumerate(['SS', 'S', 'M', 'H'])]

st.subheader("Parámetros técnicos")
col1, col2, col3, col4 = st.columns(4)
degrad = [col.number_input(f"Degradación {i+1} (%)", value=v, min_value=1.0, step=0.1)
          for i, (col, v) in enumerate(zip((col1, col2, col3, col4), [18.0, 10.0, 8.0, 7.0]))]

col1, col2, col3, col4 = st.columns(4)
tiempos = [col.number_input(f"Tiempo vuelta {i+1}", value=t, min_value=0.0, step=0.1)
           for i, (col, t) in enumerate(zip((col1, col2, col3, col4), [101.5, 102.2, 103.1, 104.2]))]

tiempo_parada_boxes = st.number_input("⏱️ Tiempo de parada en boxes (s)", value=23.0, step=0.1)
duracion_carrera = st.number_input("🏁 Duración total de la carrera (vueltas)", value=24, min_value=1)

if st.button("🚀 Ejecutar simulación"):
    try:
        race = [tiempo_parada_boxes, duracion_carrera]
        durac = duracion_neum(degrad)

        comb2 = list(itertools.product(range(len(durac)), repeat=2))
        comb3 = list(itertools.product(range(len(durac)), repeat=3))
        comb4 = list(itertools.product(range(len(durac)), repeat=4))
        combs = comb2 + comb3 + comb4
        combs = [c for c in combs if len(set(c)) > 1]
        combs = [c for c in combs if sum(durac[i] for i in c) == race[1]]

        combs_unicas = {}
        for c in combs:
            c_ordenada = tuple(sorted(c))
            vueltas_totales = sum(durac[i] for i in c)
            tiempo_total = sum(tiempos[i]*durac[i] for i in c) + race[0]*(len(c)-1)
            v_sobrante = vueltas_totales - 25
            tiempo_total -= (v_sobrante * tiempos[c[-1]])
            tiempo_total = round(tiempo_total, 1)
            if c_ordenada not in combs_unicas or combs_unicas[c_ordenada] > tiempo_total:
                combs_unicas[c_ordenada] = tiempo_total

        combs_final = {}
        for c in combs_unicas:
            tiempo_total = combs_unicas[c]
            vueltasn = [durac[i] for i in c]
            neumn = [neum[i] for i in c]
            combs_final[tuple(neumn)] = vueltasn, tiempo_total

        strat_ordenadas = sorted(combs_final.items(), key=lambda x: x[1][1])

        st.success("✅ Estrategias calculadas correctamente")
        for n, (neumaticos, (vueltas, tiempo_total)) in enumerate(strat_ordenadas):
            letra = chr(65 + n)
            st.markdown(f"### Estrategia {letra}")
            for i in range(len(neumaticos)):
                st.write(f"• Stint {i+1}: Neumático `{neumaticos[i]}`, Parada tras **{vueltas[i]}** vueltas")
            st.write(f"🕒 **Tiempo total de carrera:** `{tiempo_total} s`")
            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Error en la simulación: {e}")
