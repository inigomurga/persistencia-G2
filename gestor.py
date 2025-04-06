from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import csv
from datetime import datetime, timezone
import time
import logging
import os

# Configurar logs
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "logs.log")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuración de InfluxDB
url = "http://localhost:8086"
token = "bdBIR2X2c3Bmi6O3fkzPF0Kw18lKWrsPXLbOLbb_5jKBLXXAJOiDa7jzFGYWFoe9V-b-qmSESClzj4rniXL9Ig=="
org = "deusto"
bucket = "windDB"

# Leer y enviar datos desde un archivo CSV
def insertar_datos(dataset_path, write_api):
    i = 0
    with open(dataset_path, mode='r+', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Parsear fecha y sumar 7 años
                fecha_original = datetime.strptime(row["Date/Time"], "%d %m %Y %H:%M")
                fecha_modificada = fecha_original.replace(year=fecha_original.year + 7).replace(tzinfo=timezone.utc)
                
                point = Point("wind_data") \
                    .time(fecha_modificada) \
                    .field("LV ActivePower (kW)", float(row["LV ActivePower (kW)"])) \
                    .field("Wind Speed (m/s)", float(row["Wind Speed (m/s)"])) \
                    .field("Theoretical_Power_Curve (KWh)", float(row["Theoretical_Power_Curve (KWh)"])) \
                    .field("Wind Direction", float(row["Wind Direction"]))

                write_api.write(bucket=bucket, org=org, record=point)
                logging.info(f"La fila {i} del csv ha sido insertada.")
                time.sleep(1)
                i += 1                    
            except Exception as e:
                print(f"Error al escribir datos: {e}")
    print("Datos insertados correctamente.")

def ejecutar_consultas(client):
    query_api = client.query_api()

    # Promedio por hora - Potencia activa
    query1 = f'''
    from(bucket: "{bucket}")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "wind_data" and r._field == "LV ActivePower (kW)")
      |> aggregateWindow(every: 1h, fn: mean)
      |> yield(name: "hourly_mean_power")
    '''

    # Promedio diario - Velocidad del viento
    query2 = f'''
    from(bucket: "{bucket}")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "wind_data" and r._field == "Wind Speed (m/s)")
      |> aggregateWindow(every: 1d, fn: mean)
      |> yield(name: "daily_mean_wind")
    '''

    # Máximo semanal - Potencia teórica
    query3 = f'''
    from(bucket: "{bucket}")
      |> range(start: -90d)
      |> filter(fn: (r) => r._measurement == "wind_data" and r._field == "Theoretical_Power_Curve (KWh)")
      |> aggregateWindow(every: 1w, fn: max)
      |> yield(name: "weekly_max_theoretical_power")
    '''

    for i, query in enumerate([query1, query2, query3], start=1):
        print(f"\n--- Resultados consulta {i} ---")
        result = query_api.query(org=org, query=query)
        for table in result:
            for record in table.records:
                print(f"{record.get_time()} | {record.get_field()} | {record.get_value()}")

# Gestión del cliente y escritura
with InfluxDBClient(url=url, token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    insertar_datos("T1.csv", write_api)
    write_api.flush()

    ejecutar_consultas(client)