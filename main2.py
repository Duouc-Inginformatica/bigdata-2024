import requests
import pandas as pd
import zipfile
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

        # Descargar el archivo ZIP
        zip_file_path = os.path.join(zip_folder, f"{file_name}.zip")
        with open(zip_file_path, 'wb') as zip_file:
            zip_file.write(requests.get(file_url).content)

            print(f"Archivo ZIP '{file_name}' Descargado.")
        # Extraer el contenido del ZIP
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(zip_folder, file_name))
            print(f"Archivo ZIP '{file_name}' Descomprimido.")

# Combinar archivos en un solo DataFrame
combined_data = pd.DataFrame()

for root, dirs, files in os.walk(zip_folder):
    for file in files:
        file_path = os.path.join(root, file)
        if file_path.endswith('.csv'):  # Assuming the files are CSV, adjust accordingly
            df = pd.read_csv(file_path)
            combined_data = combined_data.append(df, ignore_index=True)

# Guardar el DataFrame combinado en un archivo Excel
excel_file_path = 'combined_data.xlsx'
combined_data.to_excel(excel_file_path, index=False)

print(f'Data combined and saved to {excel_file_path}')
