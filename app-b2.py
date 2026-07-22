import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Entrenamiento Camilo", page_icon="💪", layout="wide")

# Estilos CSS personalizados para mejorar el diseño
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #248a3d; color: white; font-weight: bold; border-radius: 8px; }
    .stButton>button:hover { background-color: #1e7030; color: white; }
    .metric-box { background-color: #1e222b; padding: 15px; border-radius: 10px; border-left: 5px solid #248a3d; margin-bottom: 15px; }
    .rutina-header { background-color: #1e222b; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# URL de lectura pública en formato CSV
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1PgY5vU-ecWChvIaACRnWmtp-GSBNEiL3-4LDu6pecOM/export?format=csv&gid=0"

# URL de escritura de Google Apps Script
API_ESCRITURA_URL = "https://script.google.com/macros/s/AKfycybGiEGEuZSd54BGB1hDaMCF-hKvjB8Qyi5SPupd_48SNw6FapsjpgS95hnA5kp4CR1HNQ/exec"

@st.cache_data(ttl=5)
def cargar_datos_nube():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if not df.empty and "Ejercicio" in df.columns:
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=["Fecha", "Letra_Rutina", "Rutina", "Ejercicio", "Series_Objetivo", "Reps_Objetivo", "Peso_Registrado", "Unidad", "Comentarios"])

if "historial_local" not in st.session_state:
    st.session_state.historial_local = cargar_datos_nube()

df_historial = st.session_state.historial_local

# Base de datos de Rutinas Estructuradas
RUTINAS = {
    "Rutina A (Pecho, Hombro, Tríceps)": [
        {"ejercicio": "Press Plano con Barra / Mancuernas", "series": 4, "reps": "8-10"},
        {"ejercicio": "Press Inclinado con Mancuernas", "series": 3, "reps": "10-12"},
        {"ejercicio": "Cruces en Polea / Aperturas", "series": 3, "reps": "12-15"},
        {"ejercicio": "Press Militar (Barra o Mancuernas)", "series": 3, "reps": "8-10"},
        {"ejercicio": "Elevaciones Laterales en Polea o Mancuerna", "series": 4, "reps": "12-15"},
        {"ejercicio": "Extensiones de Tríceps en Polea (Copa)", "series": 3, "reps": "10-12"},
        {"ejercicio": "Fondos en Paralelas / Fondos Banco", "series": 3, "reps": "Fallo controlado"}
    ],
    "Rutina B (Espalda, Bíceps, Abdomen)": [
        {"ejercicio": "Dominadas / Jalón al Pecho", "series": 4, "reps": "8-10"},
        {"ejercicio": "Remo con Barra o en Máquina", "series": 4, "reps": "8-10"},
        {"ejercicio": "Remo Unilateral con Mancuerna", "series": 3, "reps": "10-12"},
        {"ejercicio": "Pull-Over en Polea Alta", "series": 3, "reps": "12-15"},
        {"ejercicio": "Curl de Bíceps con Barra (Z)", "series": 3, "reps": "10-12"},
        {"ejercicio": "Curl Inclinado / Curl Martillo", "series": 3, "reps": "12-15"},
        {"ejercicio": "Elevaciones de Piernas / Crunches", "series": 4, "reps": "15-20"}
    ],
    "Rutina C (Pierna Completa)": [
        {"ejercicio": "Sentadilla Libre con Barra", "series": 4, "reps": "6-8"},
        {"ejercicio": "Prensa Inclinada (Leg Press)", "series": 4, "reps": "10-12"},
        {"ejercicio": "Extensiones de Cuádriceps", "series": 3, "reps": "12-15"},
        {"ejercicio": "Peso Muerto Rumano (Mancuernas o Barra)", "series": 4, "reps": "8-10"},
        {"ejercicio": "Curl Femoral Tumbado o Sentado", "series": 3, "reps": "10-12"},
        {"ejercicio": "Elevación de Talones (Pantorrillas)", "series": 4, "reps": "15-20"}
    ]
}

st.title("💪 Sistema Automatizado de Entrenamiento — Camilo")

tab_registro, tab_historial, tab_progreso = st.tabs(["📝 Registrar Entrenamiento", "📅 Historial y Calendario", "📈 Progreso Analítico"])

with tab_registro:
    st.subheader("Registrar Sesión del Día")
    
    fecha_entrenamiento = st.date_input("Fecha de la sesión", datetime.now())
    rutina_seleccionada = st.selectbox("Selecciona la Rutina a Ejecutar", list(RUTINAS.keys()))
    
    letra_rutina = "A" if "Rutina A" in rutina_seleccionada else "B" if "Rutina B" in rutina_seleccionada else "C"
    ejercicios_rutina = RUTINAS[rutina_seleccionada]
    
    st.markdown(f"<div class='rutina-header'>Cargando {rutina_seleccionada}</div>", unsafe_allow_html=True)
    
    with st.form("form_entrenamiento"):
        datos_formulario = []
        
        for idx, ej in enumerate(ejercicios_rutina):
            st.markdown(f"#### {idx+1}. {ej['ejercicio']}")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.text_input("Series Planificadas", value=str(ej['series']), disabled=True, key=f"ser_plan_{idx}")
            with col2:
                st.text_input("Reps Planificadas", value=str(ej['reps']), disabled=True, key=f"rep_plan_{idx}")
            with col3:
                peso = st.number_input("Peso Levantado", min_value=0.0, step=0.5, format="%.1f", key=f"peso_{idx}")
            with col4:
                unidad = st.selectbox("Unidad", ["Kg", "Lbs"], key=f"uni_{idx}")
                
            comentario = st.text_input("Notas / Observaciones del ejercicio", placeholder="Ej: RPE 9, última serie al fallo", key=f"com_{idx}")
            
            datos_formulario.append({
                "ejercicio": ej['ejercicio'],
                "series": ej['series'],
                "reps": ej['reps'],
                "peso": peso,
                "unidad": unidad,
                "comentario": comentario
            })
            st.markdown("---")
            
        boton_guardar = st.form_submit_button("💾 GUARDAR DÍA AUTOMÁTICAMENTE")
        
    if boton_guardar:
        filas_nuevas = []
        for dato in datos_formulario:
            filas_nuevas.append({
                "Fecha": fecha_entrenamiento.strftime("%Y-%m-%d"),
                "Letra_Rutina": letra_rutina,
                "Rutina": rutina_seleccionada,
                "Ejercicio": dato["ejercicio"],
                "Series_Objetivo": dato["series"],
                "Reps_Objetivo": dato["reps"],
                "Peso_Registrado": dato["peso"],
                "Unidad": dato["unidad"],
                "Comentarios": dato["comentario"]
            })
            
        df_nuevos = pd.DataFrame(filas_nuevas)
        
        exito_nube = True
        for _, row in df_nuevos.iterrows():
            payload = row.to_dict()
            try:
                response = requests.post(API_ESCRITURA_URL, json=payload, timeout=10)
                if response.status_code != 200:
                    exito_nube = False
            except Exception:
                exito_nube = False
                
        if exito_nube:
            st.success("¡Datos sincronizados correctamente con Google Sheets en la nube! 🚀")
            st.session_state.historial_local = pd.concat([df_nuevos, st.session_state.historial_local], ignore_index=True)
            st.rerun()
        else:
            st.warning("Se guardó localmente, pero hubo un problema al subir a Google Sheets. Revisa la URL de tu API.")

with tab_historial:
    st.subheader("Historial de Entrenamientos Recientes")
    
    if not df_historial.empty:
        st.dataframe(df_historial, use_container_width=True)
        
        st.subheader("Calendario de Asistencia Habitual")
        df_historial['Fecha'] = pd.to_datetime(df_historial['Fecha'], errors='coerce')
        dias_entrenados = df_historial['Fecha'].dropna().dt.strftime('%Y-%m-%d').unique()
        
        st.markdown(f"Has entrenado un total de **{len(dias_entrenados)} días** registrados.")
    else:
        st.info("Aún no registras entrenamientos. ¡Completa tu primera sesión en la pestaña anterior!")

with tab_progreso:
    st.subheader("Análisis de Cargas y Progreso en el Tiempo")
    
    if not df_historial.empty and len(df_historial) > 1:
        ejercicios_disponibles = df_historial['Ejercicio'].unique()
        ejercicio_grafico = st.selectbox("Selecciona un ejercicio para ver tu evolución", ejercicios_disponibles)
        
        df_filtrado = df_historial[df_historial['Ejercicio'] == ejercicio_grafico].copy()
        df_filtrado['Fecha'] = pd.to_datetime(df_filtrado['Fecha'], errors='coerce')
        df_filtrado = df_filtrado.sort_values(by='Fecha')
        
        if not df_filtrado.empty:
            # Gráfico de líneas nativo de Streamlit (sin dependencias externas)
            st.line_chart(df_filtrado.set_index('Fecha')['Peso_Registrado'])
            
            max_peso = df_filtrado['Peso_Registrado'].max()
            st.markdown(f"<div class='metric-box'>🏆 <b>Peso máximo registrado en este ejercicio:</b> {max_peso}</div>", unsafe_allow_html=True)
        else:
            st.info("Registra más días con este ejercicio para poder calcular la tendencia.")
    else:
        st.info("Necesitas registrar datos en múltiples días para generar los análisis de progreso.")

if not df_historial.empty:
    df_descarga = df_historial.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Historial Completo (CSV)",
        data=df_descarga,
        file_name=f"historial_entrenamiento_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
