# Examen_Fondeadora
Examen para la posición de Data Engineer

Dependencias de Python.


•	El examen fue realizado en un equipo con la versión 3.9.7 de python.

•	Para la instalación de los requerimientos necesarios en python para la ejecución del script, por favor correr el siquiente comando:

pip install -r requeriments.txt

•	Favor de ejecutar en la carpeta raíz donde se encuentra el script de python.



Dependencias de Base de datos.


•	Para las pruebas de conexión utilicé la versión 21.2.1 de DBeaver.

•	La base de datos empleada fue PostgreSQL 13.4, la cual fue cargada sobre un contenedor en Docker.

•	Los archivos correspondientes al respaldo se encuentran en la carpeta denominada "Databases_backups".

•	El archivo correspondiente a la base de datos cruda es el archivo "dump-postgres"

•	El archivo correspondiente a la base de datos con tablas agregadas es el archivo "dump-reduced"

•	Para poder cargar las bases de datos puede ser ejecuado el siguiente comando:

	pg_restore -d database_name db.dump

•	También puede ser cargado directamente utilizando DBeaver dando click derecho sobre una base de datos existente y seleccionando la opción "Herramientas/Restaurar backup", esto posteriormente a crear las respectivas bases de datos.



Ejecución del script.


Para ejecutar el script solo es necesario ejecutar en la termina, cmd o powershell el siguiente comando:

  python .\Examen_Fondeadora.py



En el script existen dos versiones que hacen exactamente lo mismo, sin embargo en una se realizan las operaciones de join correspondientes para generar la tabla principal que posee todos los campos de interés, mientras que la otra versión consulta de la base de datos únicamente las tablas necesarias y las carga sobre DataFrames diferentes, en este caso la operación se realiza a través de la función merge que dispone la bibleoteca Pandas en los dataframes.

De momento la versión seleccionada es la que corresponde al procesamiento puramente en python, ya que consideré que era la mejor expresión de una solución valida para el procesamiento de grandes volúmenes de datos, reduciendo la carga de procesamiento de la base de datos al realizar las consultas necesarias.

Adicional a esto, agregué un log, el cual solamente informa al usuario si se encontró algún problema con la construcción de las tablas agregadas.

En el procesamiento se puede ver que utilicé una variable para definir la dimensionalidad del problema, fue una solución que encontré y preferí construir de ese modo en lugar de generar cadenas de strings o listas puramente estáticos en funciones que realmente variar
