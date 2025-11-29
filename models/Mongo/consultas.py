
from models.Utils.validaciones import solicitar_input, Validaciones
from bson import Binary
from models.Mongo.MongoModel import MongoModel
from models.Utils.dictionaries import estado as estadoTicketDict
from models.Utils.dictionaries import prioridad as prioridadDict
from models.Mongo.Ticket import Ticket
from models.Mongo.Cliente import Cliente
from models.Mongo.Agente import Agente
from uuid import UUID

#Obtener información de agente en base a su nombre", # Mongo
def obtenerEntidades(input_message, get_function):
    result = ""
    campoObtenido = solicitar_input(input_message, canBeNone=True)
    if campoObtenido:
        entidades = get_function(campoObtenido)
        if entidades:
            result += "Información encontrada: "
            for entidad in entidades:
                result += str(entidad) + "\n"
        else:
            result += f"Ninguna información encontrada relacionada a '{campoObtenido}'\n"
    else:
        result += "Volviendo a menú principal\n"

    return result

# "Mostrar información de clientes y IDs de tickets de una empresa con tickets abiertos a partir de “x” fecha hasta la actualidad", # Mongo
def clientesConTicketsAbiertosPorFecha():
    empresa = solicitar_input("Ingrese el id de la empresa de la que quiere obtener los clientes: ", Validaciones.validar_idEmpresaExistente)
    idEmpresa = empresa.idEmpresa
    fecha = solicitar_input("Ingrese la fecha desde la que desea buscar: ", Validaciones.validar_fecha)
    pipeline = [
        {
            '$match': {
                'idEmpresa': Binary.from_uuid(idEmpresa), 
                'estado': 1, 
                'fechaCreacion': {
                    '$gte': fecha
                }
            }
        },
        {
            '$group': {
                '_id': '$idCliente',
                'tickets': {'$push': '$idTicket'} 
            }
        },
        {
            '$lookup': {
                'from': 'clientes', 
                'localField': '_id', 
                'foreignField': 'idCliente', 
                'as': 'cliente'
            }
        }
    ]

    resultStr = ""
    resultados = MongoModel.buscar_documentos_complejo('tickets', pipeline)
    if resultados:
        resultStr += f"{len(resultados)} clientes con tickets encontrados:\n"
        for resultado in resultados:
            cliente = resultado['cliente'][0]
            tickets = resultado['tickets']
            resultStr += str(Cliente.crear_desde_dict(cliente)) + "\nTickets: \n"
            for ticket in tickets:
                resultStr += "\tidTicket: " + str(UUID(bytes=ticket)) + "\n"
    else:
        resultStr = f"No se encontraron clientes de la empresa {idEmpresa} que hayan abierto tickets desde {fecha}"

    return resultStr

# "Mostrar Tickets con estado especifico por entidad", # Mongo
def ticketsEstadoPorEntidad(indicadorEntidad: str, estado: int):
    """Recibe un string 'Empresa', 'Agente' o 'Cliente' según en base a qué entidad se quiere buscar los tickets y un entero estado de ticket que se desea filtrar"""
    msj = f"Ingrese el id{indicadorEntidad} del que desea obtener tickets: "
    estado = Validaciones.validar_estadoTicket(estado)
    indicadores = ['Empresa', 'Agente', 'Cliente']
    if indicadorEntidad not in indicadores: raise ValueError(f"Indicador '{indicadorEntidad}' inválida.")

    # Para empresa
    if indicadorEntidad == indicadores[0]:
        entidad = solicitar_input(msj, Validaciones.validar_idEmpresaExistente)
        idEntidad = entidad.idEmpresa

        query = {
            "idEmpresa": Binary.from_uuid(idEntidad),
            "estado": estado
        }
    # Para agente
    elif indicadorEntidad == indicadores[1]:
        entidad = solicitar_input(msj, Validaciones.validar_idAgenteExistente)
        idEntidad = entidad.idAgente

        query = {
            "idAgente": Binary.from_uuid(idEntidad),
            "estado": estado
        }
    # Para cliente
    elif indicadorEntidad == indicadores[2]:
        entidad = solicitar_input(msj, Validaciones.validar_idClienteExistente)
        idEntidad = entidad.idCliente

        query = {
            "idCliente": Binary.from_uuid(idEntidad),
            "estado": estado
        }

    resultStr = ""
    result = MongoModel.buscar_documentos('tickets', query)
    if result:
        resultStr += f"{str(len(result))} tickets de {idEntidad} encontrados con estado '{estadoTicketDict[estado]}':\n" 
        for ticket in result:
            ticket = Ticket.crear_desde_dict(ticket)
            resultStr += f"{ticket}:" + "\n\n"

    else:
        resultStr = f"No se encontraron tickets"

    return resultStr

# "Filtrar tickets de empresa por prioridad", # Mongo
def ticketsEmpresaPrioridad():
    empresa = solicitar_input("Ingresa el idEmpresa de la empresa que quieres buscar sus tickets: ", Validaciones.validar_idEmpresaExistente)
    idEmpresa = empresa.idEmpresa
    prioridad = solicitar_input("Ingrese la prioridad a filtar: ", Validaciones.validar_prioridadTicket)

    query = {
        "idEmpresa": Binary.from_uuid(idEmpresa),
        "prioridad": prioridad
    }

    resultStr = ""
    result = MongoModel.buscar_documentos('tickets', query)
    if result:
        resultStr += f"{str(len(result))} tickets de {idEmpresa} encontrados con prioridad '{prioridadDict[prioridad]}':\n" 
        for ticket in result:
            ticket = Ticket.crear_desde_dict(ticket)
            resultStr += f"{ticket}" + "\n"

    else:
        resultStr = f"No se encontraron tickets"

    return resultStr

# "Mostrar tickets de una empresa con una antigüedad mayor a “x” fecha", # Mongo
def ticketsEmpresaAntiguedad():
    empresa = solicitar_input("Ingrese el id de la empresa de la que quiere obtener los tickets: ", Validaciones.validar_idEmpresaExistente)
    idEmpresa = empresa.idEmpresa

    fecha = solicitar_input("Ingrese la fecha desde la que desea buscar una antiguedad mayor: ", Validaciones.validar_fecha)
    query = {
        "idEmpresa": Binary.from_uuid(idEmpresa),
        "fechaCreacion": {
            "$lt": fecha
        }
    }

    resultStr = ""
    result = MongoModel.buscar_documentos('tickets', query)
    if result:
        resultStr += f"{str(len(result))} tickets de {idEmpresa} creados entes de {fecha}:\n" 
        for ticket in result:
            ticket = Ticket.crear_desde_dict(ticket)
            resultStr += f"{ticket}:" + "\n\n"

    else:
        resultStr = f"No se encontraron tickets"

    return resultStr

# "Mostrar tickets cerrados en un periodo de tiempo por agente", # Mongo
def ticketsCerradosPorPeriodoAgente():

    agente = solicitar_input("Ingrese el id del agente del que quiere obtener los tickets: ", Validaciones.validar_idAgenteExistente)
    idAgente = agente.idAgente

    fechaInicio = solicitar_input("Ingrese la fecha de inicio del periodo: ", Validaciones.validar_fecha)
    fechaFin = solicitar_input("Ingrese la fecha de finalización del periodo: ", Validaciones.validar_fecha)
    query = {
        "idAgente": Binary.from_uuid(idAgente),
        "fechaCierre": {
            "$gte": fechaInicio, 
            "$lte": fechaFin
        }
    }

    resultStr = ""
    result = MongoModel.buscar_documentos('tickets', query)
    if result:
        resultStr += f"{str(len(result))} tickets cerrados por {idAgente} entre {fechaInicio} y {fechaFin}:\n" 
        for ticket in result:
            ticket = Ticket.crear_desde_dict(ticket)
            resultStr += f"{ticket}:" + "\n\n"

    else:
        resultStr = f"No se encontraron tickets"

    return resultStr

# "Obtener la cantidad de tickets que ha cerrado cada agente de una empresa en un periodo de tiempo", # Mongo
def cantidadTicketsCerradosPorAgentes():
    empresa = solicitar_input("Ingrese el id de la empresa de la que quiere obtener la información: ", Validaciones.validar_idEmpresaExistente)
    idEmpresa = empresa.idEmpresa
    fechaInicio = solicitar_input("Ingrese la fecha de inicio del periodo: ", Validaciones.validar_fecha)
    fechaFin = solicitar_input("Ingrese la fecha de finalización del periodo: ", Validaciones.validar_fecha)

    pipeline = [
        {
            '$match': {
                'idEmpresa': Binary.from_uuid(idEmpresa), 
                'estado': 3, 
                'fechaCierre': {
                    '$gte': fechaInicio, 
                    '$lte': fechaFin
                }
            }
        }, {
            '$group': {
                '_id': '$idAgente', 
                'ticketsCerrados': {
                    '$sum': 1
                }
            }
        }, {
            '$lookup': {
                'from': 'agentes', 
                'localField': '_id', 
                'foreignField': 'idAgente', 
                'as': 'agente'
            }
        }
    ]

    resultStr = ""
    resultados = MongoModel.buscar_documentos_complejo('tickets', pipeline)
    if resultados:
        resultStr += f"{len(resultados)} agentes con tickets cerrados encontrados:\n\n"
        
        # Definir encabezados con formato
        encabezado = f"{'Nombre de agente'.ljust(25)} {'Cantidad de tickets cerrados'}\n"
        resultStr += encabezado
        resultStr += "-" * len(encabezado) + "\n"  # Línea separadora
        
        for resultado in resultados:
            nombreAgente = resultado['agente'][0]['nombre']
            cantidadTickets = resultado['ticketsCerrados']
            resultStr += f"{nombreAgente.ljust(25)} {str(cantidadTickets)}\n"

    else:
        resultStr = f"No se encontraron tickets"

    return resultStr

# Obtener la cantidad de tickets que ha cerrado un agente de una empresa en un periodo de tiempo
def cantidadTicketsCerradosPorAgente():
    empresa = solicitar_input("Ingrese el id de la empresa de la que quiere obtener la información: ", Validaciones.validar_idEmpresaExistente)
    idEmpresa = empresa.idEmpresa
    agente = solicitar_input("Ingrese el id del agente del que quiere su información: ", Validaciones.validar_idAgenteExistente)
    idAgente = agente.idAgente
    fechaInicio = solicitar_input("Ingrese la fecha de inicio del periodo: ", Validaciones.validar_fecha)
    fechaFin = solicitar_input("Ingrese la fecha de finalización del periodo: ", Validaciones.validar_fecha)

    pipeline = [
        {
            '$match': {
                'idEmpresa': Binary.from_uuid(idEmpresa), 
                'idAgente': Binary.from_uuid(idAgente),
                'estado': 3, 
                'fechaCierre': {
                    '$gte': fechaInicio, 
                    '$lte': fechaFin
                }
            }
        }, {
            '$group': {
                '_id': '$idAgente', 
                'ticketsCerrados': {
                    '$sum': 1
                }
            }
        }, {
            '$lookup': {
                'from': 'agentes', 
                'localField': '_id', 
                'foreignField': 'idAgente', 
                'as': 'agente'
            }
        }
    ]

    resultStr = ""
    resultados = MongoModel.buscar_documentos_complejo('tickets', pipeline)
    if resultados:
        resultStr += f"{len(resultados)} agentes con tickets cerrados encontrados:\n\n"
        
        # Definir encabezados con formato
        encabezado = f"{'Nombre de agente'.ljust(25)} {'Cantidad de tickets cerrados'}\n"
        resultStr += encabezado
        resultStr += "-" * len(encabezado) + "\n"  # Línea separadora
        
        for resultado in resultados:
            nombreAgente = resultado['agente'][0]['nombre']
            cantidadTickets = resultado['ticketsCerrados']
            resultStr += f"{nombreAgente.ljust(25)} {str(cantidadTickets)}\n"

    else:
        resultStr = f"No se encontraron tickets"

    return resultStr