# import models.conection as conection
import models.Mongo.populate as populate
from models.Mongo.MongoModel import MongoModel
from models.Utils.validaciones import Validaciones
from models.Utils.validaciones import solicitar_input
from models.Mongo.consultas import (
    obtenerEntidades,
    clientesConTicketsAbiertosPorFecha,
    ticketsEstadoPorEntidad,
    ticketsEmpresaPrioridad,
    ticketsEmpresaAntiguedad,
    ticketsCerradosPorPeriodoAgente,
    cantidadTicketsCerradosPorAgentes,
    cantidadTicketsCerradosPorAgente
    )
from models.Utils.crear_entidades import (
    crear_agente,
    crear_empresa,
    crear_cliente,
    crear_ticket
)
from models.Utils.actualizar_entidades import (
    actualizar_agente,
    actualizar_cliente,
    actualizar_ticket
)

# Importaciones Dgraph
import os
import pydgraph
import models.Dgraph.model as dgraph

# Importaciones Cassandra
import logging
from cassandra.cluster import Cluster
import models.Cassandra.model as CassModel
import models.Cassandra.historial as CassHistorial

#Cliente Dgraph
def get_dgraph_client():
    client_stub = pydgraph.DgraphClientStub('localhost:9080')  # Ajusta la URL según tu configuración
    return pydgraph.DgraphClient(client_stub)

def cass_session():
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    log.addHandler(handler)

    log.info("Conectando al Cluster...")
    cluster = Cluster()
    session = cluster.connect()

    return session

def printMenu(option=0):
    # Menú principal
    mm_options = {
        0: "Poblar de datos",
        1: "Registros",
        2: "Actualizaciones",
        3: "Consultas de agentes",
        4: "Consultas de clientes",
        5: "Consultas de tickets",
        6: "Consultas de empresas",
        7: "Eliminar bases de datos",
        8: "Salir"
    }

    # Registros
    mm_option1 = {
        0: "Regresar a menú principal",
        1: "Registro de Agente",
        2: "Registro de Cliente",
        3: "Registro de Ticket",
        4: "Registro de Empresa"
    }
    
    # Actualizaciones
    mm_option2 = {
        0: "Regresar a menú principal",
        1: "Actualizar Agente",
        2: "Actualizar Cliente",
        3: "Actualizar Ticket"
    }

    # Consultas de agentes
    mm_option3 = {
        0: "Regresar a menú principal",
        1: "Obtener información de agente en base a su nombre", # Mongo
        2: "Obtener información de agente en base a su ID", # Mongo
        3: "Mostrar agentes por empresa", # Dgraph
        4: "Mostrar agente por ticket", # Draph
        5: "Historial de estado en empresa de agente" # Casssandra
    }

    # Consultas de clientes
    mm_option4 = {
        0: "Regresar a menú principal",
        1: "Obtener información de cliente en base a su nombre", # Mongo
        2: "Obtener información de cliente en base a su ID", #Mongo
        3: "Mostrar información de clientes y IDs de tickets de una empresa con tickets abiertos a partir de “x” fecha hasta la actualidad", # Mongo
        4: "Mostrar clientes por empresa", # Dgraph
        5: "Mostrar cliente por ticket", # Dgraph
        6: "Historial de estado de cuenta de cliente" # Cassandra
    }

    # Consultas de tickets
    mm_option5 = {
        0:  "Regresar a menú principal", 
        1:  "Obtener información de ticket en base a su ID", # Mongo
        2:  "Mostrar Tickets con estado “Cerrado” por Agente", # Mongo
        3:  "Mostrar Tickets con estado “En proceso” por Agente", # Mongo
        4:  "Mostrar Tickets con estado “Cerrado” por Empresa", # Mongo
        5:  "Mostrar Tickets con estado “En proceso” por Empresa", # Mongo
        6:  "Mostrar Tickets con estado “Abierto” por Empresa", # Mongo
        7:  "Mostrar Tickets con estado “Cerrado” por Cliente.", # Mongo            
        8:  "Mostrar Tickets con estado “En proceso” por Cliente.", # Mongo
        9:  "Mostrar Tickets con estado “Abierto” por Cliente.", # Mongo
        10:	"Filtrar tickets de empresa por prioridad", # Mongo
        11:	"Mostrar tickets de una empresa con una antigüedad mayor a “x” fecha", # Mongo
        12:	"Mostrar tickets cerrados en un periodo de tiempo por agente", # Mongo
        13:	"Obtener la cantidad de tickets que ha cerrado cada agente de una empresa en un periodo de tiempo", # Mongo
        14:	"Obtener la cantidad de tickets que ha cerrado un agente de una empresa en un periodo de tiempo", # Mongo
        15: "Mostrar tickets por empresa", # Dgraph
        16: "Mostrar tickets por cliente", # Dgraph
        17: "Mostrar tickets de una empresa por tipo de problema ", # Dgraph
        18: "Mostrar tickets de un agente de una empresa por tipo de problema ", # Dgraph
        19: "Búsqueda de Ticket por empresa por medio de palabras clave", # Dgraph
        20: "Búsqueda de Ticket por Agente y Empresa por medio de palabras clave", # Dgraph
        21:	"Historial de comentarios de ticket en base al id del ticket", # Cassandra
        22:	"Historial de cambios en la prioridad de un ticket", # Cassandra
        23:	"Historial de asignación de agentes a un ticket", # Cassandra
        24:	"Historial de estados del ticket", # Cassandra
        25:	"Historial de tickets creados en empresa", # Cassandra
        26: "Historial de tickets creados en empresa después de x fecha" # Cassandra
    }

    # Consultas de empresas
    mm_option6 = {
        0: "Regresar a menú principal",
        1: "Obtener información de empresa en base a su nombre", # Mongo
        2: "Obtener información de empresa en base a su id", # Mongo
        3: "Mostrar ubicación de la empresa por medio de su id" # Dgraph
    }

    if option == 0:
        for key in mm_options.keys():
            print(key, '--', mm_options[key])
    if option == 1:
        for key in mm_option1.keys():
            print(key, '--', mm_option1[key])
    elif option == 2:
        for key in mm_option2.keys():
            print(key, '--', mm_option2[key])
    elif option == 3:
        for key in mm_option3.keys():
            print(key, '--', mm_option3[key])
    elif option == 4:
        for key in mm_option4.keys():
            print(key, '--', mm_option4[key])
    elif option == 5:
        for key in mm_option5.keys():
            print(key, '--', mm_option5[key])
    elif option == 6:
        for key in mm_option6.keys():
            print(key, '--', mm_option6[key])
    
client = get_dgraph_client()

# Para cargar correctamente los datos de Cassandra
session = cass_session()
def main():

    CLUSTER_IPS = os.getenv('CASSANDRA_CLUSTER_IPS', '')
    KEYSPACE = os.getenv('CASSANDRA_KEYSPACE', 'cassandra_final')
    REPLICATION_FACTOR = os.getenv('CASSANDRA_REPLICATION_FACTOR', '1')
    
    CassModel.create_keyspace(session, KEYSPACE, REPLICATION_FACTOR)
    session.set_keyspace(KEYSPACE)

    # Mientras el usuario no quiera salir, se imprime el menu
    while (True):
        printMenu(0)
        try:
            option = int(input("Seleccione una opción: "))
        except ValueError:
            print("Por favor, ingrese un número válido.")
            continue
        
        # Poblar de datos
        if option == 0:
            
            # Hacer el poblado de datos en la base de datos
            # Se puede cambiar el path a la carpeta donde se encuentran los csv
            try:
                print(populate.populate_all("data/mongo/")['resumen'])
            except FileNotFoundError as e:
                print(e)

            # Dgraph (esquema y poblado de datos)
            dgraph.set_schema(client)
            dgraph.create_data(client)

            # Cassandra
            CassModel.create_schema(session)

        # Registro de datos
        elif option == 1:
            printMenu(1)
            try:
                option = int(input("Seleccione una opción: "))
                # Regresa al menu principal
                if option == 0:
                    continue
                # Registro de Agente
                elif option == 1:
                    crear_agente(client, session)
                # Registro de Cliente
                elif option == 2:
                    crear_cliente(client, session)
                # Registro de Ticket
                elif option == 3:
                    crear_ticket(client, session)
                # Registro de Empresa
                elif option == 4:
                    crear_empresa(client, session)
                    
            except ValueError:
                print("Por favor, ingrese un número válido.")
                continue
                    
        # Actualizaciones
        elif option == 2:
            printMenu(2)
            try:
                option = int(input("Seleccione una opción: "))
                # Regresa al menu principal    
                if option == 0:
                    continue
                # Actualización de agente
                elif option == 1:
                    print(actualizar_agente(session))
                # Actualización de cliente
                elif option == 2:
                    print(actualizar_cliente(session))
                # Actualización de Ticket
                elif option == 3:
                    print(actualizar_ticket(session))

            except ValueError:
                print("Por favor, ingrese un número válido.")
                continue                
                
        # Consultas de agentes
        elif option == 3:
            printMenu(3)
            try:
                option = int(input("Seleccione una opción: "))
                if option == 0: 
                    # "Regresar a menú principal",
                    continue
                elif option == 1: 
                    # "Obtener información de agente en base a su nombre", # Mongo
                    print(obtenerEntidades("Ingrese el nombre del agente del que desea obtener información (Enter para volver): ", MongoModel.obtener_agente_por_nombre))
                
                elif option == 2: 
                    # "Obtener información de agente en base a su ID", # Mongo
                    id = input("Ingrese el ID del agente del que desea obtener información: ")
                    entidad = MongoModel.obtener_agente_por_id(id)
                    print(f"Agente encontrado: \n{entidad}\n" if entidad else f"Agente con ID {id} no encontrado")

                elif option == 3: 
                    # "Mostrar agentes por empresa", # Dgraph
                    id_empresa = input("Ingrese ID de la empresa: ")
                    result = dgraph.Agentes_por_empresa(client, id_empresa)

                elif option == 4: 
                     # "Mostrar agente por ticket", # Draph
                    id_ticket = input("Ingrese ID del ticket: ")
                    result = dgraph.Agentes_por_ticket(client, id_ticket)

                elif option == 5: 
                    # "Historial de estado en empresa de agente" # Casssandra
                    id_agente = input("Ingrese ID del agente: ")
                    CassHistorial.historial_agente(session, id_agente)

            except ValueError:
                print("Por favor, ingrese un número válido.")
                continue          
            
        # Consultas de clientes
        elif option == 4:
            printMenu(4)
            try:
                option = int(input("Seleccione una opción: "))
                # Regresa al menu principal
                if option == 0:
                    continue
                # "Obtener información de cliente en base a su nombre", # Mongo
                elif option == 1: 
                    print(obtenerEntidades("Ingrese el nombre del cliente del que desea obtener información (Enter para volver): ", MongoModel.obtener_clientes_por_nombre))

                # "Obtener información de cliente en base a su ID", #Mongo
                elif option == 2: 
                    id = input("Ingrese el ID del cliente del que desea obtener información: ")
                    entidad = MongoModel.obtener_cliente_por_id(id)
                    print(f"Cliente encontrado: \n{entidad}\n" if entidad else f"Cliente con ID {id} no encontrado")

                # "Mostrar información de clientes y IDs de tickets de una empresa con tickets abiertos a partir de “x” fecha hasta la actualidad", # Mongo
                elif option == 3: 
                    print(clientesConTicketsAbiertosPorFecha())
                    pass
                # "Mostrar clientes por empresa", # Dgraph
                elif option == 4: 
                    id_empresa = input("Ingrese ID de la empresa: ")
                    result = dgraph.Clientes_por_empresa(client, id_empresa)
                # "Mostrar cliente por ticket", # Dgraph
                elif option == 5: 
                    id_ticket = input("Ingrese ID del Ticket: ")
                    result = dgraph.Cliente_por_ticket(client, id_ticket)
                    pass
                # "Historial de estado de cuenta de cliente" # Cassandra
                elif option == 6: 
                    id_cliente = input("Ingresa ID del cliente: ")
                    CassHistorial.historial_client(session, id_cliente)

            except ValueError:
                print("Por favor, ingrese un número válido.")
                continue
                
        # Consultas de tickets
        elif option == 5:
            printMenu(5)
            try:
                option = int(input("Seleccione una opción: "))
                # Regresa al menu principal
                if option == 0:
                    continue
                # "Obtener información de ticket en base a su ID", # Mongo
                elif option == 1:
                    id = input("Ingrese el ID del ticket del que desea obtener información: ")
                    entidad = MongoModel.obtener_ticket_por_id(id)
                    print(f"Ticket encontrado: \n{entidad}\n" if entidad else f"Ticket con ID {id} no encontrado")

                # "Mostrar Tickets con estado “Cerrado” por Agente", # Mongo
                elif option == 2:
                    print(ticketsEstadoPorEntidad('Agente', 3))
                # "Mostrar Tickets con estado “En proceso” por Agente", # Mongo
                elif option == 3:
                    print(ticketsEstadoPorEntidad('Agente', 2))
                # "Mostrar Tickets con estado “Cerrado” por Empresa", # Mongo
                elif option == 4:
                    print(ticketsEstadoPorEntidad('Empresa', 3))
                # "Mostrar Tickets con estado “En proceso” por Empresa", # Mongo
                elif option == 5:
                    print(ticketsEstadoPorEntidad('Empresa', 2))
                # "Mostrar Tickets con estado “Abierto” por Empresa", # Mongo
                elif option == 6:
                    print(ticketsEstadoPorEntidad('Empresa', 1))
                # "Mostrar Tickets con estado “Cerrado” por Cliente.", # Mongo            
                elif option == 7:
                    print(ticketsEstadoPorEntidad('Cliente', 3))
                # "Mostrar Tickets con estado “En proceso” por Cliente.", # Mongo
                elif option == 8:
                    print(ticketsEstadoPorEntidad('Cliente', 2))
                # "Mostrar Tickets con estado “Abierto” por Cliente.", # Mongo
                elif option == 9:
                    print(ticketsEstadoPorEntidad('Cliente', 1))
                # "Filtrar tickets de empresa por prioridad", # Mongo
                elif option == 10:
                    print(ticketsEmpresaPrioridad())
                # "Mostrar tickets de una empresa con una antigüedad mayor a “x” fecha", # Mongo
                elif option == 11:
                    print(ticketsEmpresaAntiguedad())
                # "Mostrar tickets cerrados en un periodo de tiempo por agente", # Mongo
                elif option == 12:
                    print(ticketsCerradosPorPeriodoAgente())
                # "Obtener la cantidad de tickets que ha cerrado cada agente de una empresa en un periodo de tiempo", # Mongo
                elif option == 13:
                    print(cantidadTicketsCerradosPorAgentes())
                # "Obtener la cantidad de tickets que ha cerrado un agente de una empresa en un periodo de tiempo", # Mongo
                elif option == 14:
                    print(cantidadTicketsCerradosPorAgente())
                # "Mostrar tickets por empresa", # Dgraph
                elif option == 15:
                    id_empresa = input("Ingrese ID de la empresa: ")
                    result = dgraph.Tickets_por_empresa(client, id_empresa)
                # "Mostrar tickets por cliente", # Dgraph
                elif option == 16:
                    nombre_cliente = input("Ingrese el nombre del cliente: ")
                    result = dgraph.Tickets_por_cliente(client, nombre_cliente)
                # "Mostrar tickets de una empresa por tipo de problema ", # Dgraph
                elif option == 17:
                    id_empresa = input("Ingrese ID de la empresa: ")
                    tipo_problema = input("Ingrese tipo de problema (en formato numérico): ")
                    result = dgraph.Tickets_por_empresa_tipo(client, id_empresa, tipo_problema)
                # "Mostrar tickets de un agente de una empresa por tipo de problema ", # Dgraph
                elif option == 18:
                    id_agente = input("Ingrese ID del Agente: ")
                    tipo_problema = input("Ingrese tipo de problema (en formato numérico): ")
                    result = dgraph.Tickets_por_agente_tipo(client, id_agente, tipo_problema)
                # "Búsqueda de Ticket por empresa por medio de palabras clave", # Dgraph
                elif option == 19:
                    id_empresa = input("Ingrese ID de la empresa: ")
                    tipo_problema = input("Ingrese palabras clave: ")
                    result = dgraph.Ticket_por_empresa_palabras(client, id_empresa, palabras_clave)
                # "Búsqueda de Ticket por Agente y Empresa por medio de palabras clave", # Dgraph
                elif option == 20:
                    id_empresa = input("Ingrese ID de la empresa: ")
                    id_agente = input("Ingrese ID del agente: ")
                    palabras_clave = input("Ingrese palabras clave: ")
                    result = dgraph.Ticket_por_agente_empresa_palabras(client, id_empresa, id_agente, palabras_clave)
                # "Historial de comentarios de ticket en base al id del ticket", # Cassandra
                elif option == 21:
                    id_ticket = input("Ingrese ID del ticket: ")
                    CassHistorial.historial_comments(session, id_ticket)
                # "Historial de cambios en la prioridad de un ticket", # Cassandra
                elif option == 22:
                    id_ticket = input("Ingrese ID del ticket: ")
                    CassHistorial.historial_prio(session, id_ticket)
                # "Historial de asignación de agentes a un ticket", # Cassandra
                elif option == 23:
                    id_ticket = input("Ingrese ID del ticket: ")
                    CassHistorial.historial_age(session, id_ticket)
                # "Historial de estados del ticket", # Cassandra
                elif option == 24:
                    id_ticket = input("Ingrese ID del ticket: ")
                    CassHistorial.historial_est(session, id_ticket)
                # "Historial de tickets creados en empresa" # Cassandra
                elif option == 25:
                    id_empresa = input("Ingrese ID de la empresa: ")
                    CassHistorial.historial_empresa(session, id_empresa)
                # "Historial de tickets creados en empresa en x fecha" # Cassandra
                elif option == 26:
                    id_empresa = input("Ingrese ID de la empresa: ")
                    fecha = solicitar_input("Ingrese la fecha desde la que desea buscar: ", Validaciones.validar_fecha)
                    CassHistorial.historial_empresa_fecha(session, id_empresa, fecha)
            
            except ValueError:
                print("Por favor, ingrese un número válido.")
                continue
                
        # Consultas de empresas
        elif option == 6:
            printMenu(6)
            try:
                option = int(input("Seleccione una opción: "))
                # Regresa al menu principal
                if option == 0:
                    continue
                # "Obtener información de empresa en base a su nombre", # Mongo
                elif option == 1:
                    print(obtenerEntidades("Ingrese el nombre de la empresa de la que desea obtener información (Enter para volver): ", MongoModel.obtener_empresa_por_nombre))

                # "Obtener información de empresa en base a su id", # Mongo
                elif option == 2:
                    id = input("Ingrese el ID de la empresa de la que desea obtener información: ")
                    entidad = MongoModel.obtener_empresa_por_id(id)
                    print(f"Empresa encontrado: \n{entidad}\n" if entidad else f"Empresa con ID {id} no encontrada")

                # "Mostrar ubicación de la empresa por medio de su id" # Dgraph
                elif option == 3:
                    id_empresa = input("Ingrese ID de la empresa: ")
                    result = dgraph.Direccion_empresa_por_id(client, id_empresa)

            except ValueError:
                print("Por favor, ingrese un número válido.")
                continue            
                
        # Eliminar bases de datos
        elif option == 7:
            while (option not in ['y', 'Y', 'n', 'N']):
                option = input("Seguro que quiere eliminar todo? y/n: ")
                if option in ['y', 'Y']:
                    print(MongoModel.eliminar_db())
                    dgraph.drop_all(client)
                    CassModel.delete_schema(session)
                    print("Datos eliminados correctamente.")
                if option in ['n', 'N']:
                    print("Volviendo a menú sin eliminar nada\n")
        # Salir
        elif option == 8:
            print("Saliendo...")
            break

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error:', e)
