import pandas as pd
import numpy as np
import database_connection as dbc
import logging

#Esta parte del código se encarga de realizar la unión de las tablas de modo que cada campo de la tabla principal posee su respectivo conjunto de datos
#localizado en su respectiva tabla
def mergeAndCleanTable(rental_cars, trade_mark_type, rental_moment_data, delivery_moment_data, car_type, motor_type, office_data):
    logging.info('Combinando dataframes de las tablas de la base de datos')
    #Combina y limpia las tablas "office data" y "rental moment"    
    merged_rental_moment_table = rental_moment_data.merge(office_data, how='inner', left_on = 'office_data_id', right_on = 'office_data_id')
    merged_rental_moment_table = merged_rental_moment_table[['rental_car_id', 'name', 'rmd_date']]

    #Combina y limpia las tablas "office data" y "delivery moment"
    merged_delivery_moment_table = delivery_moment_data.merge(office_data, how='inner', left_on = 'office_data_id', right_on = 'office_data_id')
    merged_delivery_moment_table = merged_delivery_moment_table[['rental_car_id', 'name', 'dmd_date']]

    #Combina y limpia la tabla principal y la tabla "mark type"    
    merged_rental_cars = rental_cars.merge(trade_mark_type, how='inner', left_on = 'trade_mark_type_id', right_on = 'trade_mark_type_id')
    merged_rental_cars = merged_rental_cars[['rental_car_id', 'motor_type_id', 'car_type_id', 'year', 'model', 'tmt_description_es']]

    #Combina y limpia la tabla principal y la combinación de las tablas "office data" y "rental moment", se soluciona un problema con un nombre repetido 
    merged_rental_cars = merged_rental_cars.merge(merged_rental_moment_table, how='inner', left_on = 'rental_car_id', right_on = 'rental_car_id')
    merged_rental_cars = merged_rental_cars[['rental_car_id', 'motor_type_id', 'car_type_id', 'year', 'model', 'tmt_description_es', 'name', 'rmd_date']]
    merged_rental_cars = merged_rental_cars.rename(columns={'name': 'departure_office'})

    #Se realiza la misma operación que antes, utilizando la tabla "delivery moment"
    merged_rental_cars = merged_rental_cars.merge(merged_delivery_moment_table, how='inner', left_on = 'rental_car_id', right_on = 'rental_car_id')
    merged_rental_cars = merged_rental_cars[['motor_type_id', 'car_type_id', 'year', 'model', 'tmt_description_es', 'departure_office', 'name', 'rmd_date', 'dmd_date']]
    merged_rental_cars = merged_rental_cars.rename(columns={'name': 'entrance_office'})

    #Combina y limpia la tabla principal y la tabla "car type"
    merged_rental_cars = merged_rental_cars.merge(car_type, how='inner', left_on = 'car_type_id', right_on = 'car_type_id')
    merged_rental_cars = merged_rental_cars[['motor_type_id', 'ct_description_es' , 'year', 'model', 'tmt_description_es', 'departure_office', 'entrance_office', 'rmd_date', 'dmd_date']]

    #Combina y limpia la tabla principal y la tabla "motor type"
    merged_rental_cars = merged_rental_cars.merge(motor_type, how='inner', left_on = 'motor_type_id', right_on = 'motor_type_id')
    merged_rental_cars = merged_rental_cars[['mt_description_es', 'ct_description_es' , 'year', 'model', 'tmt_description_es', 'departure_office', 'entrance_office', 'rmd_date', 'dmd_date']]

    if not merged_rental_cars.empty:
        logging.info('Dataframe general creado exitosamente')
    else:
        logging.info('Hubo un problema al generar el dataframe general')
    #Se renombran las columnas por nombres más manejables
    merged_rental_cars = merged_rental_cars.rename(columns={'mt_description_es': 'motor_type', 'ct_description_es': 'car_type' , 'tmt_description_es': 'trade_mark', 'rmd_date': 'rental_days'})
    return merged_rental_cars


#Con el fin de conocer la diferencia entre el tiempo de salida y entrada de los veículos rentados, se genera una resta en el formato de fecha utilizado
#en la base de datos
def calculateRentalDays(data):
    logging.info('Calculando días de renta')
    data['rental_days'] = data['dmd_date'] - data['rental_days']
    data['rental_days'] = data['rental_days']/np.timedelta64(1,'D')
    data['rental_days'] = data['rental_days'].astype(int)
    return data    
    

#Se reducen las columnas a fin de obtener únicamente las necesarias para realizar el proceso establecido, en este punto se genera el dataframe agrupado
def cleanTable(data, option):
    logging.info('Proceso de limpieza de los datos, generando dataframes reducidos y suma de los dias rentados')
    #Se genera la tabla considerando las diferentes dimensionalidades
    finish_columns_names = ["trade_mark"]
    if option >= 1:
        finish_columns_names.append("model")
    if option >= 2:
        finish_columns_names.append("year")
    if option >= 3:
        finish_columns_names.append("car_type")
    if option >= 4:
        finish_columns_names.append("motor_type")
    if option >= 5:
        finish_columns_names.append("departure_office")
    if option >= 6:
        finish_columns_names.append("entrance_office")
    group_by_condition = list(finish_columns_names)
    finish_columns_names.append("rental_days")
    
    #Se reduce el número de columnas
    data = data[finish_columns_names]
    
    #Crea la tabla agrupada, se utiliza la dimensionalidad para definir qué columnas emplear para la agrupación
    datagroup = pd.DataFrame(data.groupby(by=group_by_condition)["rental_days"].sum())
    if not datagroup.empty:
        logging.info('El dataframe reducido fue generado exitosamente')
    else:
        logging.info('Hubo un problema al generar el dataframe reducido')
    return datagroup
    

#Opción de solución principal, la segunda es resultado de un error al desear realizar todas las operaciones sin generar ninguna operación dentro de
#python
def optionOne():
    logging.basicConfig(filename='Log_opcion_1_examen.log', level=logging.INFO)
    logging.info('Iniciado')
    database_name = "postgres"
    engine = dbc.openConnection(database_name)
    rental_cars, trade_mark_type, rental_moment_data, delivery_moment_data, car_type, motor_type, office_data = dbc.getTables(engine)
    merged_rental_cars = mergeAndCleanTable(rental_cars, trade_mark_type, rental_moment_data, delivery_moment_data, car_type, motor_type, office_data)
    data = calculateRentalDays(merged_rental_cars)
    data1 = cleanTable(merged_rental_cars, 1)
    data2 = cleanTable(merged_rental_cars, 2)
    data3 = cleanTable(merged_rental_cars, 3)
    data4 = cleanTable(merged_rental_cars, 4)
    data5 = cleanTable(merged_rental_cars, 5)
    data6 = cleanTable(merged_rental_cars, 6)
    database_name = "reduced"
    engine_reduced = dbc.openConnection(database_name)
    dbc.saveData(engine_reduced, data1, "acc_table_1")
    dbc.saveData(engine_reduced, data2, "acc_table_2")
    dbc.saveData(engine_reduced, data3, "acc_table_3")
    dbc.saveData(engine_reduced, data4, "acc_table_4")
    dbc.saveData(engine_reduced, data5, "acc_table_5")
    dbc.saveData(engine_reduced, data6, "acc_table_6")
    logging.info('Finalizado')

#Primera opción desarrollada para la solución del problema, existe una versión basada en la ejecución de un único query dependiendo de la dimensionalidad. 
#La solución se volvía conflictiva al ejecutarse en paralelo con las versiones que se muestran en este scrip
def optionTwo():
    logging.basicConfig(filename='Log_opcion_2_examen.log', level=logging.INFO)
    logging.info('Iniciado')
    database_name = "postgres"
    engine_original = dbc.openConnection(database_name)
    data1 = dbc.getData(engine_original, 1)
    data2 = dbc.getData(engine_original, 2)
    data3 = dbc.getData(engine_original, 3)
    data4 = dbc.getData(engine_original, 4)
    data5 = dbc.getData(engine_original, 5)
    data6 = dbc.getData(engine_original, 6)
    database_name = "reduced"
    engine_reduced = dbc.openConnection(database_name)
    dbc.saveData(engine_reduced, data1, "acc_table_1")
    dbc.saveData(engine_reduced, data2, "acc_table_2")
    dbc.saveData(engine_reduced, data3, "acc_table_3")
    dbc.saveData(engine_reduced, data4, "acc_table_4")
    dbc.saveData(engine_reduced, data5, "acc_table_5")
    dbc.saveData(engine_reduced, data6, "acc_table_6")
    logging.info('Finalizado')

if __name__ == "__main__":
    optionOne()
#    optionTwo()
