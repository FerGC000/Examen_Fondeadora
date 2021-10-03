import pandas as pd
from sqlalchemy import create_engine
import logging

#Esta operación es utilizada en la opción 2, en esta función se construye el query que traerá la información compuesta por 
#las diferentes tablas de la base de datos
def getQuery(option):
    logging.info('Generando query')
    select_command = ""
    join_command = """INNER JOIN trade_mark_type AS tmt ON (rc.trade_mark_type_id = tmt.trade_mark_type_id) 
        INNER JOIN rental_moment_data AS rmd ON (rc.rental_car_id = rmd.rental_car_id) 
        INNER JOIN delivery_moment_data AS dmd ON (rc.rental_car_id = dmd.rental_car_id) """
    if option >= 1:
        select_command += "tmt.description_es, rc.model, "
    if option >= 2:
        select_command += "rc.\"year\", "
    if option >= 3:
        select_command += "ct.description_es, "
        join_command += "INNER JOIN car_type AS ct ON (rc.car_type_id = ct.car_type_id) "
    if option >= 4:
        select_command += "mt.description_es, "
        join_command += "INNER JOIN motor_type AS mt ON (rc.motor_type_id = mt.motor_type_id) "
    if option >= 5:
        select_command += "od1.\"name\", "
        join_command += "INNER JOIN office_data AS od1 ON (rmd.office_data_id = od1.office_data_id) "
    if option >= 6:
        select_command += "od2.\"name\", "
        join_command += "INNER JOIN office_data AS od2 ON (dmd.office_data_id = od2.office_data_id) "
    return "SELECT " + select_command + "DATE_PART('day', dmd.\"date\" - rmd.\"date\") FROM rental_cars AS rc " + join_command + ";"


#Esta operación es utilizada en la opción 2, en esta se reducen las columnas a fin de obtener únicamente las necesarias para realizar el proceso establecido, 
#en este punto se genera el dataframe agrupado
def getDataGroup(data, option):
    logging.info('Generando dataframes reducidos, agrupacion para la suma de dias rentado')
    #Generate the table using different dimensionalities
    columns = ["trade_mark"]
    datagroup = pd.DataFrame();
    if option >= 1:
        columns.append("model")
    if option >= 2:
        columns.append("year")
    if option >= 3:
        columns.append("car_type")
    if option >= 4:
        columns.append("motor_type")
    if option >= 5:
        columns.append("departure_office")
    if option >= 6:
        columns.append("entrance_office")
    group_by_condition = list(columns)
    columns.append("rental_days")
    data.columns = columns

    #Create the data group, the columns to group is defined by the dimensionality
    datagroup = pd.DataFrame(data.groupby(by=group_by_condition)["rental_days"].sum())
    if not datagroup.empty:
        logging.info('El dataframe reducido fue generado exitosamente')
    else:
        logging.info('Hubo un problema al generar el dataframe reducido')
    return datagroup


#Esta operación es utilizada en la opción 2, se encarga de obtener la tabla compuesta a través de la ejecución de un query 
#que posee joins para facilitar el procesamiento de los datos    
def getData(engine, option): 
    logging.info('Obteniendo informacion de la base de datos')
    postgreSQL_select_Query = getQuery(option)
    data = pd.DataFrame(engine.execute(postgreSQL_select_Query).fetchall())
    if not data.empty:
        logging.info('Datos obtenidos correctamente')
    else:
        logging.info('Hubo un problema al obtener los datos de la base de datos')
    return getDataGroup(data, option)


#En esta función se realiza la conexión a la base de datos utilizando psycopg2, la base de datos utilizada es postgresql
def openConnection(database):
    logging.info('Conectandose a la base de datos')
    engine = create_engine('postgresql+psycopg2://postgres:Fergc00@localhost:5432/' + database)
    if engine:
        logging.info('Conexion realizada exitosamente')
    else:
        logging.info('Hubo un problema al conectarse a la base de datos')
    return engine;


#Esta función se encarga de enviar la información a las tablas agregadas
def saveData(engine, data, table_name):
    logging.info('Enviando tabla ' + table_name + ' a la base de datos')    
    conn = engine.connect()
    trans = conn.begin()
    data.to_sql(name=table_name, con=engine, if_exists='replace')
    trans.commit()


#Esta operación es utilizada en la opción 1, se encarga de obtener todas las tablas empleadas en la base de datos para los 
#registros de veículos rentados 
def getTables(engine):
    logging.info('Obteniendo datos de las tablas de la base de datos')
    rental_cars = pd.DataFrame(engine.execute("SELECT * from rental_cars").fetchall())
    trade_mark_type = pd.DataFrame(engine.execute("SELECT * from trade_mark_type").fetchall())
    rental_moment_data = pd.DataFrame(engine.execute("SELECT * from rental_moment_data").fetchall())
    delivery_moment_data = pd.DataFrame(engine.execute("SELECT * from delivery_moment_data").fetchall())
    car_type = pd.DataFrame(engine.execute("SELECT * from car_type").fetchall())
    motor_type = pd.DataFrame(engine.execute("SELECT * from motor_type").fetchall())
    office_data = pd.DataFrame(engine.execute("SELECT * from office_data").fetchall())
 
    #Se asignan nombres a las columnas, ésto con el fin de facilitar el manejo posterior de la información
    rental_cars.columns = ['rental_car_id', 'motor_type_id', 'trade_mark_type_id', 'car_type_id', 'niv', 'year', 'model', 'expedition', 'capacity'];
    trade_mark_type.columns = ['trade_mark_type_id', 'code', 'tmt_description_us', 'tmt_description_es', 'is_active'];
    rental_moment_data.columns = ['rental_car_id', 'office_data_id', 'rmd_date'];
    delivery_moment_data.columns = ['rental_car_id', 'office_data_id', 'dmd_date'];
    car_type.columns = ['car_type_id', 'code', 'ct_description_us', 'ct_description_es', 'is_active'];
    motor_type.columns = ['motor_type_id', 'code', 'mt_description_us', 'mt_description_es', 'is_active'];
    office_data.columns = ['office_data_id', 'name', 'address_1', 'address_2', 'cp', 'city', 'state'];
    
    return rental_cars, trade_mark_type, rental_moment_data, delivery_moment_data, car_type, motor_type, office_data