import models.Utils.dictionaries as dictionaries
import uuid
from bson import Binary
from models.Utils.validaciones import (Validaciones, solicitar_input)
from models.Mongo.MongoModel import MongoModel
from models.Mongo.Agente import Agente as MongoAgente
from models.Mongo.Cliente import Cliente as MongoCliente
from models.Mongo.Ticket import Ticket as MongoTicket

# Importaciones de cassandra
import models.Cassandra.model as CassModel
from datetime import datetime

def actualizar_agente(session):
    cambios_agente_dict = {}

    estadosEnEmpresa = dictionaries.estadoEnEmpresa

    # Obtener el agente
    try: 
        mongo_agente: MongoAgente = solicitar_input("Ingrese el ID del agente a modificar: ", Validaciones.validar_idAgenteExistente)
        if not mongo_agente:
            raise ValueError(f"Error: Debe introducir un id de agente")

        cambios_agente_dict['idAgente'] = mongo_agente.idAgente

        telefono = solicitar_input("Ingrese el nuevo teléfono del agente (dejar en blanco para no editarlo): ", Validaciones.validar_telefono, True)
        estadoEnEmpresa = solicitar_input(f"Ingrese el número del nuevo estado en la empresa del agente (dejar en blanco para no editarlo) \n\tEstados posibles: {estadosEnEmpresa}): ", Validaciones.validar_estadoEnEmpresa, True) 

        # Asignar valores a diccionario
        if telefono:
            cambios_agente_dict['telefono'] = telefono
        if estadoEnEmpresa:
            cambios_agente_dict['estadoEnEmpresa'] = estadoEnEmpresa

        # Actualizar agentes 
        # Actualizar en MongoDB
        nuevo_mongo_agente = MongoModel.actualizar_agente(mongo_agente.idAgente, cambios_agente_dict)
        
        # Insertar en Cassandra
        nuevo_cass_agente = CassModel.actualizar_agente(session, cambios_agente_dict)

        return f"Agente: \n{mongo_agente}\n\nActualizado con éxito en Mongo a:\n{nuevo_mongo_agente} \n\n{nuevo_cass_agente} en Cassandra"
    
    except Exception as e:
        print(f"Error en la actualización de agente: {e}")

def actualizar_cliente(session):
    cambios_cliente_mongo = {}
    cambios_cliente_cass = {}

    estadosCuenta = dictionaries.estadoCuenta

    # Obtener el cliente
    mongo_cliente: MongoCliente = solicitar_input("Ingrese el ID del cliente a modificar: ", Validaciones.validar_idClienteExistente)

    cambios_cliente_cass['idCliente'] = mongo_cliente.idCliente

    telefono = solicitar_input("Ingrese el nuevo teléfono del cliente (dejar en blanco para no editarlo): ", Validaciones.validar_telefono, True)
    correo = solicitar_input("Ingrese el nuevo correo del cliente (dejar en blanco para no editarlo): ", Validaciones.validar_formato_correo, True)
    estadoCuenta = solicitar_input(f"Ingrese el número del nuevo estado de cuenta del cliente (dejar en blanco para no editarlo) \n\tEstados posibles: {estadosCuenta}): ", Validaciones.validar_estadoCuenta, True) 

    # Asignar valores diccionario
    if telefono:
        cambios_cliente_mongo['telefono'] = telefono
    if correo:
        cambios_cliente_mongo['correo'] = correo
    if estadoCuenta:
        cambios_cliente_mongo['estadoCuenta'] = estadoCuenta
        cambios_cliente_cass['estado'] = estadoCuenta

    # Actualizar cliente 
    try:
        # Actualizar en MongoDB
        nuevo_mongo_cliente = MongoModel.actualizar_cliente(mongo_cliente.idCliente, cambios_cliente_mongo)

        # Insertar en Cassandra
        nuevo_cass_cliente = CassModel.actualizar_cliente(session, cambios_cliente_cass)
        return f"Cliente: \n{mongo_cliente}\n\nActualizado con éxito en Mongo a:\n{nuevo_mongo_cliente} \n\n{nuevo_cass_cliente} en Cassandra"

    except Exception as e:
        print(f"Error en la actualización de cliente: {e}")

def actualizar_ticket(session):
    cambios_ticket_mongo = {}
    cambios_ticket_cass = {}

    estadosTicket = dictionaries.estado
    prioridadesTicket = dictionaries.prioridad

    # Obtener el cliente
    mongo_ticket: MongoTicket = solicitar_input("Ingrese el ID del ticket a modificar: ", Validaciones.validar_idTicketExistente)
    cambios_ticket_cass['idTicket'] = mongo_ticket.idTicket

    fechaCierre = solicitar_input("Inserte la fecha en la que cierra el ticket (enter para no establecer/no editar): ", Validaciones.validar_fecha, True)
    estadoTicket = solicitar_input(f"Ingrese el número del nuevo estado del ticket (dejar en blanco para no editarlo) \n\tEstados posibles: {estadosTicket}): ", Validaciones.validar_estadoTicket, True) 
    idAgente = solicitar_input("Inserte el id del nuevo agente que se le asignará el ticket (dejar en blanco para no editar): ", Validaciones.validar_idAgenteExistente, True)
    if idAgente:
        idAgente = idAgente.idAgente
    prioridad = solicitar_input(f"Inserte la nueva prioridad del ticket (Dar enter para no editar) \n\tPrioridades posibles: {prioridadesTicket}): ", Validaciones.validar_prioridadTicket, True)
    comentario = input(f"Ingrese el nuevo comentario para el ticket (dejar en blanco para no agregar): ")

    # Agregar valores modificados a diccionario de cambios si fueron modificados
    if fechaCierre:
        cambios_ticket_mongo['fechaCierre'] = fechaCierre
        cambios_ticket_cass['fecha'] = fechaCierre
    else:
        cambios_ticket_cass['fecha'] = datetime.today()
    if estadoTicket:
        cambios_ticket_mongo['estadoTicket'] = estadoTicket
        cambios_ticket_cass['estado'] = estadoTicket
    if idAgente:
        cambios_ticket_mongo['idAgente'] = Binary.from_uuid(idAgente)
        cambios_ticket_cass['idAgente'] = idAgente
    if prioridad:
        cambios_ticket_mongo['prioridad'] = prioridad
        cambios_ticket_cass['prioridad'] = prioridad
    if comentario:
        cambios_ticket_mongo['comentarios'] = mongo_ticket.comentarios + [comentario]
        cambios_ticket_cass['comentario'] = comentario

    # Actualizar diccionario
    try:
        # Actualizar en MongoDB
        nuevo_mongo_ticket = MongoModel.actualizar_ticket(mongo_ticket.idTicket, cambios_ticket_mongo)

        # Insertar en Cassandra
        nuevo_cass_ticket = CassModel.actualizar_ticket(session, cambios_ticket_cass)
        return f"Ticket: \n{mongo_ticket}\n\nActualizado con éxito en Mongo a:\n{nuevo_mongo_ticket} \n\n {nuevo_cass_ticket} en Cassandra"

    except Exception as e:
        print(f"Error en la actualización de ticket: {e}")