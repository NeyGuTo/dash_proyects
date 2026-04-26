import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np

st.set_page_config(page_title="Dashboard Farmacia", layout="wide")
st.title("📊 Dashboard de Control de Farmacia")

# Subida de ambos archivos Excel
uploaded_file_1 = st.file_uploader("Carga el archivo de Productos Esenciales", type=["xlsx"], key="file1")
uploaded_file_2 = st.file_uploader("Carga el archivo de Productos del Almacén", type=["xlsx"], key="file2")

# Función para limpiar las descripciones (eliminar detalles irrelevantes)
def limpiar_descripcion(descripcion):
    # Eliminar detalles como "COMO SAL SODICA", "X 100 DET", etc.
    descripcion_limpia = re.sub(r' - (COMO|EQUIV|X \d{1,3} DET).*', '', descripcion)  # Eliminar palabras y detalles extra
    descripcion_limpia = re.sub(r'\(.*\)', '', descripcion_limpia)  # Eliminar cualquier cosa entre paréntesis
    descripcion_limpia = descripcion_limpia.strip()  # Eliminar espacios al principio y final
    return descripcion_limpia.lower()  # Convertir a minúsculas para comparar sin importar mayúsculas/minúsculas

# Función para normalizar las concentraciones
def normalizar_concentracion(concentracion):
    # Verificar si el valor es NaN o está vacío
    if pd.isna(concentracion) or concentracion == "":
        return ""  # Devolver una cadena vacía si la concentración está vacía o es NaN

    if isinstance(concentracion, str):  # Verificar si es una cadena
        # Eliminar caracteres no numéricos y estandarizar los formatos
        concentracion = re.sub(r'[^\d\.\-\%\+]', '', concentracion)  # Mantener solo números, puntos, y % o +
        if '%' in concentracion:
            concentracion = concentracion.replace('%', '')  # Eliminar el símbolo de porcentaje para comparar como número
    else:
        concentracion = str(concentracion)  # Convertir a cadena si no lo es
    
    return concentracion

if uploaded_file_1 and uploaded_file_2:
    # Leer los dos archivos Excel
    df_essential = pd.read_excel(uploaded_file_1)
    df_warehouse = pd.read_excel(uploaded_file_2)

    # Preprocesar los productos esenciales
    df_essential.columns = df_essential.columns.str.strip()
    # Limpiar las descripciones y normalizar concentraciones de los productos esenciales
    df_essential['Descripcion_med'] = df_essential['Descripcion_med'].apply(limpiar_descripcion)
    df_essential['Concentracion'] = df_essential['Concentracion'].apply(normalizar_concentracion)

    # Preprocesar los productos del almacén
    df_warehouse.columns = df_warehouse.columns.str.strip()
    # Limpiar las descripciones y normalizar concentraciones de los productos del almacén
    df_warehouse['Descripcion_med'] = df_warehouse['Descripcion_med'].apply(limpiar_descripcion)
    df_warehouse['Concentracion'] = df_warehouse['Concentracion'].apply(normalizar_concentracion)

    # Comparación de las descripciones y concentraciones
    coincidencias = df_warehouse[
        df_warehouse['Descripcion_med'].isin(df_essential['Descripcion_med']) & 
        df_warehouse['Concentracion'].isin(df_essential['Concentracion'])
    ]

    # Mostrar los resultados de la comparación
    st.subheader("🔍 Productos coincidentes entre el almacén y los productos esenciales")
    st.dataframe(
        coincidencias[["Descripcion_med", "Concentracion"]]
        .reset_index(drop=True),
        use_container_width=True
    )

    # KPIs - Número de coincidencias
    total_coincidencias = len(coincidencias)
    st.metric("Productos coincidentes", total_coincidencias)

    # Si hay coincidencias, contar las coincidencias de cada producto
    if total_coincidencias > 0:
        # Contar las ocurrencias de cada producto
        coincidencias_count = coincidencias['Descripcion_med'].value_counts()

        # Crear gráfico de barras horizontales
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(coincidencias_count.index, coincidencias_count.values, color='mediumseagreen')
        ax.invert_yaxis()
        ax.set_xlabel("Número de coincidencias")
        ax.set_title("Productos coincidentes entre el almacén y los productos esenciales")
        st.pyplot(fig)

    # Mostrar cuántas concentraciones vacías hay en los productos esenciales
    st.write("Concentraciones vacías en los productos esenciales:", df_essential['Concentracion'].isna().sum())
    # Mostrar cuántas concentraciones vacías hay en los productos del almacén
    st.write("Concentraciones vacías en los productos del almacén:", df_warehouse['Concentracion'].isna().sum())

else:
    st.info("📂 Por favor, sube los dos archivos Excel para comenzar.")
