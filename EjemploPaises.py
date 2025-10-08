import streamlit as st
import pandas as pd
import requests
import time 

# --- CONFIGURACIÓN DE LA FUNCIÓN DE API (Se mantiene igual) ---

@st.cache_data(show_spinner=False)
def get_country_data(country_list):
    results = []
    progress_bar = st.progress(0, text="Realizando consultas a la API...")
    
    total_requests = len(country_list)

    for i, country_name in enumerate(country_list):
        # ... (Lógica de la API y manejo de errores se mantiene igual) ...
        try:
            url = f"https://restcountries.com/v3.1/name/{country_name}?fields=name,capital,population"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            
            results.append({
                "País Solicitado": country_name,
                "Nombre Oficial": data[0]['name']['official'],
                "Capital": data[0]['capital'][0] if 'capital' in data[0] and data[0]['capital'] else 'N/A',
                "Población": data[0]['population']
            })

        except requests.exceptions.RequestException as e:
            results.append({
                "País Solicitado": country_name,
                "Nombre Oficial": "ERROR",
                "Capital": str(e),
                "Población": "ERROR"
            })

        progress_percentage = (i + 1) / total_requests
        progress_bar.progress(progress_percentage, text=f"Consultando: {country_name} ({i+1}/{total_requests} completado)")

    progress_bar.empty()
    return pd.DataFrame(results)


# --- CÓDIGO PRINCIPAL DE STREAMLIT (Los cambios están en la sección de descarga) ---

st.title("Consulta de API a Gran Escala con Archivo Excel 🚀")

uploaded_file = st.file_uploader("Carga tu archivo de Excel (con columna 'País')", type="xlsx")

if uploaded_file is not None:
    df_input = pd.read_excel(uploaded_file)
    st.subheader("Datos Cargados")
    st.dataframe(df_input.head())

    if st.button("Ejecutar Consultas"):
        if "País" in df_input.columns:
            country_list = df_input["País"].astype(str).tolist()
            
            with st.spinner("Procesando las consultas, ¡esto puede tardar unos minutos! ☕"):
                df_results = get_country_data(country_list)
            
            st.subheader("Resultados de la API")
            st.dataframe(df_results)
            
            # 1. MODIFICACIÓN: FUNCIÓN PARA CONVERTIR A EXCEL
            @st.cache_data
            def convert_df_to_excel(df):
                # Usamos BytesIO para guardar el archivo Excel en memoria
                import io
                output = io.BytesIO()
                # Escribe el DataFrame a Excel sin el índice
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='ResultadosAPI')
                # Retorna los bytes del archivo
                return output.getvalue()

            excel_data = convert_df_to_excel(df_results)

            # 2. MODIFICACIÓN: BOTÓN DE DESCARGA
            st.download_button(
                label="Descargar Resultados en EXCEL",
                data=excel_data,
                file_name='resultados_api.xlsx', # Cambiar la extensión
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', # CAMBIO DE MIME
            )

        else:
            st.error("El archivo de Excel debe contener una columna llamada 'País'.")