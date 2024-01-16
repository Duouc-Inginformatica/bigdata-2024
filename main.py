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

    # Crear una carpeta para almacenar los archivos TXT
    txt_folder = 'archivos_txt'
    os.makedirs(txt_folder, exist_ok=True)

    # Crear una carpeta para almacenar los archivos Excel individuales
    excel_folder = 'archivos_excel'
    os.makedirs(excel_folder, exist_ok=True)

    # Descargar y descomprimir todos los archivos ZIP
    for resource in resources:
        if resource['format'] == 'ZIP':
            zip_url = resource['url']
            zip_filename = os.path.join(zip_folder, f"{resource['name']}.zip")

            try:
                # Descargar el archivo ZIP
                zip_response = requests.get(zip_url)
                zip_response.raise_for_status()

                # Guardar el archivo ZIP
                with open(zip_filename, 'wb') as zip_file:
                    zip_file.write(zip_response.content)

                print(f"Archivo ZIP '{zip_filename}' descargado.")

                # Descomprimir el archivo ZIP en la carpeta 'archivos_txt'
                with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                    zip_ref.extractall(txt_folder)

                print(f"Archivo ZIP '{zip_filename}' descomprimido y archivos TXT generados en la carpeta 'archivos_txt'.")

            except (requests.exceptions.RequestException, zipfile.BadZipFile) as e:
                print(f"Error al procesar el archivo ZIP '{zip_url}': {e}")
                continue  # Pasar al siguiente archivo ZIP si hay un error

    # Procesar archivos de texto (todos los archivos .txt) y generar archivos Excel individuales
    for root, dirs, files in os.walk(txt_folder):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                table_data = pd.read_csv(file_path, delimiter=',')  # Modifica el delimitador según tu archivo

                # Guardar los datos en un archivo Excel individual en la carpeta 'archivos_excel'
                output_filename = os.path.join(excel_folder, f"{file}.xlsx")
                with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
                    table_data.to_excel(writer, index=False)

                print(f"Archivo de texto '{file}' procesado y guardado en Excel en la carpeta 'archivos_excel'.")

    # Combinar todos los archivos Excel individuales en un archivo Excel general en la carpeta 'out'
    output_general = os.path.join('out', 'archivo_general.xlsx')
    writer = pd.ExcelWriter(output_general, engine='openpyxl')
    for root, dirs, files in os.walk(excel_folder):
        for file in files:
            file_path = os.path.join(root, file)
            df = pd.read_excel(file_path, engine='openpyxl')
            df.to_excel(writer, sheet_name=f"{file.replace('.xlsx', '')}", index=False)

    writer.save()
    print("Proceso completado. Archivos ZIP descargados, descomprimidos, archivos Excel generados y archivo general creado.")
else:
    print("No hay recursos disponibles para procesar.")
