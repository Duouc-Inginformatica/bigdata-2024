import requests
import pandas as pd
import os
import zipfile

# Definiciones
package_id = 33245
url = f"https://datos.gob.cl/api/action/package_show?id={package_id}"
zip_folder = 'archivos_zip'
unpack_folder = 'unpack'
csv_folder = 'archivos_csv'

# Crear carpetas si no existen
os.makedirs(zip_folder, exist_ok=True)
os.makedirs(unpack_folder, exist_ok=True)
os.makedirs(csv_folder, exist_ok=True)

# Descargar archivos ZIP
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    resources = data['result']['resources']

    for resource in resources:
        if resource['format'].lower() == 'zip':
            file_name = resource['name'].strip() + '.zip'
            file_url = resource['url']
            file_path = os.path.join(zip_folder, file_name)
            
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as file:
                    file.write(requests.get(file_url).content)
                print(f"Archivo '{file_name}' descargado.")
            else:
                print(f"Archivo '{file_name}' ya existe, saltando la descarga.")
except (requests.exceptions.RequestException, ValueError) as e:
    print(f"Error al obtener el JSON: {e}")

# Procesar y combinar archivos descomprimidos
all_dataframes = []
for zip_file in os.listdir(zip_folder):
    if zip_file.endswith('.zip'):
        zip_path = os.path.join(zip_folder, zip_file)
        zip_unpack_folder = os.path.join(unpack_folder, zip_file[:-4]) # Carpeta específica para este ZIP
        os.makedirs(zip_unpack_folder, exist_ok=True)

        dataframes_zip = []  # DataFrames para todos los zips

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(zip_unpack_folder)
            print(f"Archivo '{zip_file}' descomprimido en '{zip_unpack_folder}'.")

            # Procesar y combinar archivos .txt de este ZIP
            for file_name in os.listdir(zip_unpack_folder):
                if file_name.endswith('.txt'):
                    file_path = os.path.join(zip_unpack_folder, file_name)
                    try:
                        df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
                        dataframes_zip.append(df)
                    except Exception as e:
                        print(f"No se pudo procesar el archivo {file_name}: {e}")

            if dataframes_zip:
                # crear un conjuntos de datos de los TXT a csv
                df_zip = pd.concat(dataframes_zip, ignore_index=True)
                zip_csv_file = os.path.join(csv_folder, zip_file[:-4] + '.csv')
                df_zip.to_csv(zip_csv_file, index=False, encoding='utf-8')
                print(f"Archivo CSV creado para ZIP '{zip_file}': {zip_csv_file}")
                all_dataframes.append(df_zip)

        except zipfile.BadZipFile:
            print(f"El archivo '{zip_file}' no es un ZIP válido o está corrupto.")

# Concatenar y exportar a CSV unificado
if all_dataframes:
    final_df = pd.concat(all_dataframes, ignore_index=True)
    combined_csv_file = os.path.join(csv_folder, 'datos_unificados.csv')
    final_df.to_csv(combined_csv_file, index=False, encoding='utf-8')
    print(f"Archivo CSV combinado creado: {combined_csv_file}")
else:
    print("No se encontraron archivos para procesar.")
