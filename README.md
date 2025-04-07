# Reto Persistencia

**Jon Cañadas, Iñigo Murga y Mikel García**

## Explicación

Este proyecto es un reto de persistencia, en el que se implementará una base de datos de tipo InfluxDB. Para la realización hemos seguido los siguientes pasos:

1. Creación del contenedor con la base de datos InfluxDB:

Hemos configurado los parámetros para el contenedor de Influx, para acceder a la base de datos hemos establecido el puerto 8086 y la imagen de InfluxDB, será la última versión. Además se ha implementado un volumen para persistir los datos.

2. Descargar e insertar los datos a la base de datos:

El enlace del dataset es el siguiente: https://www.kaggle.com/datasets/berkerisen/wind-turbine-scada-dataset. Tras descargarlo, primero se creó un script que volcaba los datos línea a línea, después se pensó que sería mejor opción volcar todos los datos de una sola vez, ya que es un dataset estático. Antes de añadir los datos, se ha modificado la fecha, para que sea más actual.

3. Visualizar los datos:

Los datos insertados se visualizan mediante las gráficas que proporciona InfluxDB.

4. Calcular agregaciones:

Se calculan las siguientes agregaciones: promedio por hora de potencia activa, promedio diario de la velocidad del viento y máximo semanal de potencia teórica. Los cálculos se realizan a través de consultas a la base de datos.



## Instalación

1. Clonar el repositorio:
    ```bash
    git clone https://github.com/inigomurga/persistencia-G2.git
    ```
2. Navega al directorio del proyecto:
    ```bash
    cd persistencia-G2
    ```
3. Construir y lanzar el contenedor Docker:
    ```bash
    docker-compose up -d
    ```
4. Configurar la base de datos InfluxDB:
    Hay que configurar el usuario, la contraseña, organización y bucket para que nos de un token personal.

## Uso

Tras configurar la base de datos, hay que establecer los parámetros en el script de Python, ya que no se puede establecer un token fijo. Después se lanzará el script de python, que además de volcar el dataset en la base de datos, realiza las consultas para calcular las agregaciones.
Existen dos scripts, gestor.py que lo que haría sería cada segundo cargar un registro del dataset a la base de datos y realizar las consultas, y el gestor_envioMasivo.py que en vez de ir registro a registro volcaría todos los datos de una vez.

## Posibles vías de mejora

En vez de tener que cambiar cada vez los parámetros del script, se podría hacer de forma más automatizada. Un ejemplo sería exportar el token como variable de entorno y acceder a él a través de variables.

## Problemas / Retos encontrados

A la hora de insertar los datos después de haber modificado el campo fecha para actualizarla, nos ha dado muchos errores con el formato que finalmente se han podido solventar.
Otro error que nos ha dado ha sido a la hora de lanzar el script de volcado, ya que no establecía conexión al lanzarlo desde WSL, así que lo hemos tenido que lanzar  mano desde el sistema operativo Windows.


## Alternativas posibles

Como alternativa se podría haber utilizado otro tipo de base de datos, pero hemos considerado que la más adecuada sería InfluxDB por que cada registro tiene un campo que monitoriza a hora de lectura.
