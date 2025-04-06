from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import csv
from datetime import datetime, timezone

# Configuración de InfluxDB
url = "http://localhost:8086"
token = "0Tz-yZkl1yCgl_vV5gnhClcK18FfCL3-Dk0vhs3v-SPsqJv0tDq3Fgv4kn3TQAZPi2dzzrLWO4tioNeM_YQfbQ==-b-qmSESClzj4rniXL9Ig=="
org = "deusto"
bucket = "windDB"

# Leer y enviar datos desde un archivo CSV
def insertar_datos(dataset_path, write_api):
    with open(dataset_path, mode='r') as file:
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
            except Exception as e:
                print(f"Error al escribir datos: {e}")
    print("Datos insertados correctamente.")

# Consultas agregadas usando Flux
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

# Gestión del cliente y escritura + consultas
with InfluxDBClient(url=url, token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    insertar_datos("T1.csv", write_api)
    write_api.flush()

    ejecutar_consultas(client)