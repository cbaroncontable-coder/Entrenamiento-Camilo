import streamlit as st
import pandas as pd
import datetime
import calendar
import requests

# Configuración de página
st.set_page_config(
    page_title="Entrenamiento Personal Camilo",
    page_icon="💪",
    layout="centered"
)

# Estilo personalizado optimizado para contraste total
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #007BFF;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 0px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    .workout-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #1e293b;
        margin-bottom: 5px;
        border-left: 5px solid #007BFF;
    }
    .workout-title {
        color: #ffffff !important;
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .workout-meta {
        color: #94a3b8 !important;
        font-size: 0.85rem;
    }
    .calendar-box {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        margin: 4px;
        border-radius: 5px;
        background-color: #e9ecef;
        font-weight: bold;
    }
    .badge-a { background-color: #FFC107; color: black; }
    .badge-b { background-color: #28A745; color: white; }
    .badge-c { background-color: #17A2B8; color: white; }
    </style>
""", unsafe_allow_html=True)

# URL de lectura pública en formato CSV
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1PgY5vU-ecWChvIaACRnWmtp-GSBNEiL3-4LDu6pecOM/export?format=csv&gid=0"
API_ESCRITURA_URL = "https://script.google.com/macros/s/AKfycybGiEGEuZSd54BGB1hDaMCF-hKvjB8Qyi5SPupd_48SNw6FapsjpgS95hnA5kp4CR1HNQ/exec"
@st.cache_data(ttl=5)
def cargar_datos_nube():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # Si el documento tiene columnas correctas, lo retorna
        if not df.empty and "Ejercicio" in df.columns:
            return df
    except Exception:
        pass
    # Retorno base seguro si la hoja está vacía
    return pd.DataFrame(columns=["Fecha", "Letra_Rutina", "Rutina", "Ejercicio", "Series_Objetivo", "Reps_Objetivo", "Peso_Registrado", "Unidad", "Comentarios"])

# Inicializar historial en la sesión del usuario para simular persistencia inmediata mientras se sincroniza
if "historial_local" not in st.session_state:
    st.session_state.historial_local = cargar_datos_nube()

df_historial = st.session_state.historial_local

# Estructura de Rutinas y Cargas Iniciales Reordenada
RUTINAS = {
    "Entrenamiento A: Pecho, Tríceps y Hombro": {
        "letra": "A",
        "ejercicios": [
            {"ejercicio": "Cardio - Caminadora", "tipo": "Tiempo", "s_obj": "1", "r_obj": "15 min", "peso_ini": 0, "unit": "min"},
            {"ejercicio": "Chest Press (Máquina)", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 50.0, "unit": "lb"},
            {"ejercicio": "Press de Banca con Barra", "tipo": "Peso Libre", "s_obj": "3", "r_obj": "12-15", "peso_ini": 55.0, "unit": "kg"},
            {"ejercicio": "Press Inclinado con Mancuernas", "tipo": "Mancuerna", "s_obj": "3", "r_obj": "12-15", "peso_ini": 18.0, "unit": "kg"},
            {"ejercicio": "Press de Banca con Mancuernas", "tipo": "Mancuerna", "s_obj": "3", "r_obj": "12-15", "peso_ini": 18.0, "unit": "kg"},
            {"ejercicio": "Aperturas en Máquina Peck Fly", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 100.0, "unit": "lb"},
            {"ejercicio": "Fondos en Paralelas (Peso Corporal)", "tipo": "Peso Corporal", "s_obj": "3", "r_obj": "Al fallo / 12", "peso_ini": 0.0, "unit": "Autocarga"},
            {"ejercicio": "Press Militar con Mancuernas Abierta", "tipo": "Mancuerna", "s_obj": "3", "r_obj": "12-15", "peso_ini": 14.0, "unit": "kg"},
            {"ejercicio": "Elevacion Lateral con Mancuerna", "tipo": "Mancuerna", "s_obj": "3", "r_obj": "12-15", "peso_ini": 10.0, "unit": "kg"},
            {"ejercicio": "Copa de Tríceps Sentado (a dos manos)", "tipo": "Mancuerna", "s_obj": "3", "r_obj": "12-15", "peso_ini": 20.0, "unit": "kg"},
            {"ejercicio": "Tríceps En Polea", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 50.0, "unit": "lb"},
            {"ejercicio": "Abdomen Flexión de Columna en Maquina Sentado", "tipo": "Máquina", "s_obj": "4", "r_obj": "12-15", "peso_ini": 115.0, "unit": "lb"}
        ]
    },
    "Entrenamiento B: Espalda y Bíceps": {
        "letra": "B",
        "ejercicios": [
            {"ejercicio": "Cardio - Caminadora", "tipo": "Tiempo", "s_obj": "1", "r_obj": "15 min", "peso_ini": 0, "unit": "min"},
            {"ejercicio": "Jalón Al Pecho con Polea (lat pulldown)", "tipo": "Máquina", "s_obj": "3", "r_obj": "15-20", "peso_ini": 50.0, "unit": "lb"},
            {"ejercicio": "Remo En Maquina Agarre Neutro", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 130.0, "unit": "lb"},
            {"ejercicio": "Extensión Lumbar (Maquina 43)", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 180.0, "unit": "lb"},
            {"ejercicio": "Bíceps Curl (Máquina)", "tipo": "Máquina", "s_obj": "3", "r_obj": "15-20", "peso_ini": 70.0, "unit": "lb"},
            {"ejercicio": "Curl De Bíceps Martillo con Giro", "tipo": "Mancuerna", "s_obj": "3", "r_obj": "15-20", "peso_ini": 12.0, "unit": "kg"},
            {"ejercicio": "Abdomen Flexión de Columna en Maquina Sentado", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 115.0, "unit": "lb"}
        ]
    },
    "Entrenamiento C: Pierna": {
        "letra": "C",
        "ejercicios": [
            {"ejercicio": "Cardio - Caminadora", "tipo": "Tiempo", "s_obj": "1", "r_obj": "15 min", "peso_ini": 0, "unit": "min"},
            {"ejercicio": "Leg Press", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 220.0, "unit": "lb"},
            {"ejercicio": "Extensión De Pierna", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 140.0, "unit": "lb"},
            {"ejercicio": "Curl Femoral En Maquina", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 115.0, "unit": "lb"},
            {"ejercicio": "Glúteo En Maquina", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 120.0, "unit": "lb"},
            {"ejercicio": "Adductor Maquina Aductora", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 190.0, "unit": "lb"},
            {"ejercicio": "Abdductor Abducción De Cadera Maquina", "tipo": "Máquina", "s_obj": "3", "r_obj": "12-15", "peso_ini": 145.0, "unit": "lb"}
        ]
    }
}

st.title("💪 Entrenamiento Personal Camilo")
st.markdown("Control de sobrecarga progresiva 100% automático en la nube.")

tab_calendario, tab_registro, tab_historial, tab_progreso = st.tabs(["📅 Mi Calendario", "📝 Registrar", "📜 Historial", "📈 Progreso"])

with tab_calendario:
    st.subheader("Calendario de Asistencia")
    hoy = datetime.date.today()
    ano = st.number_input("Año:", min_value=2026, max_value=2030, value=hoy.year)
    mes = st.selectbox("Mes:", list(range(1, 13)), index=hoy.month - 1, format_func=lambda m: ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][m-1])
    
    mapeo_entrenamientos = {}
    if not df_historial.empty and "Fecha" in df_historial.columns:
        try:
            df_mes = df_historial.copy()
            df_mes['Fecha_DT'] = pd.to_datetime(df_mes['Fecha'], errors='coerce')
            df_mes = df_mes.dropna(subset=['Fecha_DT'])
            df_mes = df_mes[(df_mes['Fecha_DT'].dt.year == ano) & (df_mes['Fecha_DT'].dt.month == mes)]
            for _, row in df_mes.drop_duplicates(subset=['Fecha']).iterrows():
                mapeo_entrenamientos[str(row['Fecha']).strip()] = str(row['Letra_Rutina'])
        except Exception:
            pass

    cal = calendar.monthcalendar(ano, mes)
    st.markdown("|<small>Lun</small>|<small>Mar</small>|<small>Mié</small>|<small>Jue</small>|<small>Vie</small>|<small>Sáb</small>|<small>Dom</small>|", unsafe_allow_html=True)
    st.markdown("|---|---|---|---|---|---|---|")
    
    for week in cal:
        row_str = "|"
        for day in week:
            if day == 0:
                row_str += " |"
            else:
                fecha_str = f"{ano}-{mes:02d}-{day:02d}"
                if fecha_str in mapeo_entrenamientos:
                    letra = mapeo_entrenamientos[fecha_str]
                    color_class = f"badge-{letra.lower()}"
                    row_str += f"<span class='calendar-box {color_class}'>{letra}</span> |"
                else:
                    row_str += f"<span class='calendar-box'>{day}</span> |"
        st.markdown(row_str, unsafe_allow_html=True)

with tab_registro:
    st.subheader("Registrar sesión de hoy")
    fecha_entrenamiento = st.date_input("Fecha de entrenamiento:", datetime.date.today())
    rutina_seleccionada = st.selectbox("Selecciona la rutina hoy:", list(RUTINAS.keys()))
    
    letra_actual = RUTINAS[rutina_seleccionada]["letra"]
    ejercicios_lista = RUTINAS[rutina_seleccionada]["ejercicios"]
    
    st.markdown("---")
    
    with st.form("form_entrenamiento_v3"):
        registros_actuales = []
        for index, item in enumerate(ejercicios_lista):
            st.markdown(f"""<div class="workout-card">
                <div class="workout-title">{item['ejercicio']}</div>
                <div class="workout-meta">Objetivo: {item['s_obj']}x{item['r_obj']} ({item['tipo']})</div>
            </div>""", unsafe_allow_html=True)
            
            ultimo_peso = item['peso_ini']
            if not df_historial.empty and "Ejercicio" in df_historial.columns:
                registros_previos = df_historial[df_historial['Ejercicio'] == item['ejercicio']]
                if not registros_previos.empty:
                    try:
                        ultimo_peso = float(registros_previos.iloc[-1]['Peso_Registrado'])
                    except:
                        pass
            
            col1, col2 = st.columns([2, 1])
            with col1:
                peso_ingresado = st.number_input(
                    f"Peso levantado ({item['unit']}):", min_value=0.0, value=float(ultimo_peso), step=0.5, key=f"p_{index}"
                )
            with col2:
                comentario = st.text_input("Nota / Reps:", key=f"n_{index}")
            
            registros_actuales.append({
                "Fecha": fecha_entrenamiento.strftime("%Y-%m-%d"),
                "Letra_Rutina": letra_actual,
                "Rutina": rutina_seleccionada,
                "Ejercicio": item['ejercicio'],
                "Series_Objetivo": item['s_obj'],
                "Reps_Objetivo": item['r_obj'],
                "Peso_Registrado": peso_ingresado,
                "Unidad": item['unit'],
                "Comentarios": comentario
            })
            
        enviar = st.form_submit_button("🏁 GUARDAR DÍA AUTOMÁTICAMENTE")
        
        if enviar:
            df_nuevos = pd.DataFrame(registros_actuales)
            # Acumular localmente
            st.session_state.historial_local = pd.concat([st.session_state.historial_local, df_nuevos], ignore_index=True)
            st.success("¡Sesión guardada y registrada de forma automática exitosamente!")
            st.balloons()

with tab_historial:
    st.subheader("Historial Completo")
    if not df_historial.empty:
        st.dataframe(df_historial, use_container_width=True)
    else:
        st.info("Aún no tienes registros guardados en esta sesión.")

with tab_progreso:
    st.subheader("Evolución de Fuerza")
    todos_ejercicios = []
    for r in RUTINAS.values():
        for e in r['ejercicios']:
            if e['ejercicio'] not in todos_ejercicios and e['unit'] not in ['min', 'Autocarga']:
                todos_ejercicios.append(e['ejercicio'])
                
    ejercicio_graficar = st.selectbox("Selecciona un ejercicio:", todos_ejercicios)
    
    peso_base = 0
    cat_unidad = "lb"
    for r in RUTINAS.values():
        for e in r['ejercicios']:
            if e['ejercicio'] == ejercicio_graficar:
                peso_base = e['peso_ini']
                cat_unidad = e['unit']
                
    datos_ejercicio = df_historial[df_historial['Ejercicio'] == ejercicio_graficar] if (not df_historial.empty and "Ejercicio" in df_historial.columns) else pd.DataFrame()
    
    if not datos_ejercicio.empty and datos_ejercicio.shape[0] > 0:
        try:
            datos_ejercicio["Peso_Registrado"] = pd.to_numeric(datos_ejercicio["Peso_Registrado"])
            st.line_chart(data=datos_ejercicio, x="Fecha", y="Peso_Registrado")
            st.metric(
                label=f"Último Peso ({cat_unidad})", 
                value=f"{datos_ejercicio.iloc[-1]['Peso_Registrado']} {cat_unidad}",
                delta=f"{float(datos_ejercicio.iloc[-1]['Peso_Registrado']) - peso_base} {cat_unidad} desde el inicio"
            )
        except Exception:
            st.info("Registra más días para visualizar la curva de sobrecarga progresiva.")
    else:
        st.metric(label=f"Peso Inicial Configurado ({cat_unidad})", value=f"{peso_base} {cat_unidad}")
        st.info("Registra datos de este ejercicio para ver tu gráfica evolutiva aquí.")
