import requests
import pandas as pd
import os

# Obtener el JSON de la API
package_id = 33245
url = f"https://datos.gob.cl/api/action/package_show?id={package_id}"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    resources = data['result']['resources']
except (requests.exceptions.RequestException, ValueError) as e:
    print(f"Error al obtener el JSON: {e}")
    resources = []

if resources:
    # Crear una carpeta para almacenar los archivos ZIP
    zip_folder = 'archivos_zip'
    os.makedirs(zip_folder, exist_ok=True)

    # Iterar sobre los recursos
    for resource in resources:
        file_name = resource['name']
        file_url = resource['url']

        # Limpieza del nombre del archivo para evitar problemas con espacios
        cleaned_file_name = file_name.strip()

        # Verificar si el archivo ya existe
        file_path = os.path.join(zip_folder, cleaned_file_name)
        if not os.path.exists(file_path):
            # Descargar el archivo solo si no existe
            with open(file_path, 'wb') as file:
                file.write(requests.get(file_url).content)
            print(f"Archivo '{cleaned_file_name}' Descargado.")
        else:
            print(f"Archivo '{cleaned_file_name}' ya existe, saltando la descarga.")

# Combinar archivos en un solo DataFrame
dfs = []

for root, dirs, files in os.walk(zip_folder):
    for file in files:
        file_path = os.path.join(root, file)
        if file_path.lower().endswith('.txt'):  # Assuming all files are in text format
            # Read the text file and append it to the list of DataFrames
            df = pd.read_csv(file_path, delimiter='\t')  # Adjust the delimiter if necessary
            dfs.append(df)

# Divide el DataFrame en trozos más pequeños
chunk_size = 50000  # Número de filas por trozo
num_chunks = len(dfs) // chunk_size + 1

# Crear una carpeta para almacenar los archivos temporales
tempolares_folder = 'tempolares'
os.makedirs(tempolares_folder, exist_ok=True)

for i in range(num_chunks):
    start_idx = i * chunk_size
    end_idx = min((i + 1) * chunk_size, len(dfs))
    chunk_df = pd.concat(dfs[start_idx:end_idx], ignore_index=True)

    # Guarda cada trozo como un archivo CSV separado en la carpeta "tempolares"
    csv_chunk_path = os.path.join(tempolares_folder, f'combined_data_chunk_{i + 1}.csv')
    chunk_df.to_csv(csv_chunk_path, index=False)
    print(f'Data chunk {i + 1} saved to {csv_chunk_path}')
