import streamlit as st
import pandas as pd
import requests
import time # Útil para implementar pausas

# --- CONFIGURACIÓN DE LA FUNCIÓN DE API ---

# Usar st.cache_data para evitar recalcular la función si los inputs son los mismos
@st.cache_data(show_spinner=False)
def get_country_data(country_list):
    results = []
    # Usamos st.progress para mostrar al usuario el avance de las 3000 consultas
    progress_bar = st.progress(0, text="Realizando consultas a la API...")
    
    total_requests = len(country_list)

    for i, country_name in enumerate(country_list):
        try:
            # 1. Construir la URL de la API
            url = f"https://restcountries.com/v3.1/name/{country_name}?fields=name,capital,population"
            
            # 2. Realizar la solicitud HTTP
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Lanza un error para códigos 4xx/5xx

            # 3. Procesar los datos (REST Countries devuelve una lista)
            data = response.json()
            
            # 4. Extraer la información relevante
            results.append({
                "País Solicitado": country_name,
                "Nombre Oficial": data[0]['name']['official'],
                "Capital": data[0]['capital'][0] if 'capital' in data[0] and data[0]['capital'] else 'N/A',
                "Población": data[0]['population']
            })
            
            # --- LÍMITE DE TASA (Si usas una API con límite por minuto, como OpenWeatherMap) ---
            # if (i + 1) % 60 == 0: # Si ya hiciste 60 peticiones...
            #     time.sleep(60)     # ...espera un minuto para el siguiente lote.

        except requests.exceptions.RequestException as e:
            # Manejar errores de conexión o límites de la API
            results.append({
                "País Solicitado": country_name,
                "Nombre Oficial": "ERROR",
                "Capital": str(e),
                "Población": "ERROR"
            })

        # Actualizar la barra de progreso
        progress_percentage = (i + 1) / total_requests
        progress_bar.progress(progress_percentage, text=f"Consultando: {country_name} ({i+1}/{total_requests} completado)")

    progress_bar.empty() # Eliminar la barra cuando termine
    return pd.DataFrame(results)


# --- CÓDIGO PRINCIPAL DE STREAMLIT ---

st.title("Consulta de API 🚀")

uploaded_file = st.file_uploader("Carga tu archivo de Excel (con columna 'País')", type="xlsx")

if uploaded_file is not None:
    # Cargar el archivo
    df_input = pd.read_excel(uploaded_file)
    st.subheader("Datos Cargados")
    st.dataframe(df_input.head())

    if st.button("Ejecutar Consultas"):
        # Asegúrate de que la columna existe y es del tamaño correcto (o toma las primeras 3000)
        if "País" in df_input.columns:
            country_list = df_input["País"].astype(str).tolist()
            
            with st.spinner("Procesando las consultas, ¡esto puede tardar unos minutos! ☕"):
                df_results = get_country_data(country_list)
            
            st.subheader("Resultados de la API")
            st.dataframe(df_results)
            
            # Opción para descargar los resultados
            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df(df_results)

            st.download_button(
                label="Descargar Resultados en CSV",
                data=csv,
                file_name='resultados_api.csv',
                mime='text/csv',
            )

        else:
            st.error("El archivo de Excel debe contener una columna llamada 'País'.")