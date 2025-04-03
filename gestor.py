from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import csv
from datetime import datetime, timezone

# Configuración de InfluxDB
url = "http://localhost:8086"
token = "bdBIR2X2c3Bmi6O3fkzPF0Kw18lKWrsPXLbOLbb_5jKBLXXAJOiDa7jzFGYWFoe9V-b-qmSESClzj4rniXL9Ig=="
org = "deusto"
bucket = "windDB"

# Leer y enviar datos desde un archivo CSV
def insertar_datos(dataset_path, write_api):
    with open(dataset_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                point = Point("wind_data") \
                    .time(datetime.now(timezone.utc)) \
                    .field("LV ActivePower (kW)", float(row["LV ActivePower (kW)"])) \
                    .field("Wind Speed (m/s)", float(row["Wind Speed (m/s)"])) \
                    .field("Theoretical_Power_Curve (KWh)", float(row["Theoretical_Power_Curve (KWh)"])) \
                    .field("Wind Direction", float(row["Wind Direction"]))

                write_api.write(bucket=bucket, org=org, record=point)
            except Exception as e:
                print(f"Error al escribir datos: {e}")
    print("Datos insertados correctamente.")

# Gestión del cliente y escritura
with InfluxDBClient(url=url, token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    insertar_datos("T1.csv", write_api)
    write_api.flush()
