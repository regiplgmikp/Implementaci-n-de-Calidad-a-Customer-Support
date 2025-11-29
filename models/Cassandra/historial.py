# HISTORIALES DE CASSANDRA
import uuid
import datetime

# Diccionarios a utilizar
from models.Utils.dictionaries import estadoCuenta as estadoCuentaDict
from models.Utils.dictionaries import estadoEnEmpresa as estadoEmpresaDict
from models.Utils.dictionaries import prioridad as prioridadDict
from models.Utils.dictionaries import estado as estadoDict

# 1. Historial de comentarios del ticket en base al ID
def historial_comments(session, id_ticket_str):
    # Convertimos id_ticket_str a uuid
    try:
        id_ticket = uuid.UUID(id_ticket_str)

    except ValueError:
        print("No existe un ticket con ese ID")
        return

    # Query con el historial de comentarios
    SELECT_TICKET_COMMENTS = """ 
        SELECT idTicket, toDate(fecha) as fecha, comentario 
        FROM ticket_com
        WHERE idTicket = %s
    """

    rows = session.execute(SELECT_TICKET_COMMENTS, (id_ticket,))
    # Resultados del query
    print(f"📝 Historial de comentarios para el ticket {id_ticket_str}:")
    for row in rows:
        print(f"- {row.fecha} | {row.comentario}")

# 2. Historial de cambios en la prioridad del ticket
def historial_prio(session, id_ticket_str):
    # Convertimos id_ticket_str a uuid
    try:
        id_ticket = uuid.UUID(id_ticket_str)

    except ValueError:
        print("No existe un ticket con ese ID")
        return

    # Query con el historial de prioridad
    SELECT_TICKET_PRIO = """ 
        SELECT idTicket, toDate(fecha) as fecha, prioridad
        FROM ticket_prio
        WHERE idTicket = %s
    """

    rows = session.execute(SELECT_TICKET_PRIO, (id_ticket,))
    # Resultados del query
    print(f"📝 Historial de prioridades para el ticket {id_ticket_str}:")
    for row in rows:
        ticket_prio = prioridadDict[row.prioridad]
        print(f"- {row.fecha} | {ticket_prio}")

# 3. Historial de asignacion de agentes a un ticket
def historial_age(session, id_ticket_str):
    # Convertimos id_ticket_str a uuid
    try:
        id_ticket = uuid.UUID(id_ticket_str)

    except ValueError:
        print("No existe un ticket con ese ID")
        return

    # Query con el historial de agentes
    SELECT_TICKET_AGE = """
        SELECT idTicket, toDate(fecha) as fecha, idAgente
        FROM ticket_age
        WHERE idTicket = %s
    """

    rows = session.execute(SELECT_TICKET_AGE, (id_ticket,))
    # Resultados del query
    print(f"📝 Historial de agentes del ticket {id_ticket_str}:")
    for row in rows:
        print(f"- {row.fecha} | {row.idagente}")

# 4. Historial de estados del ticket
def historial_est(session, id_ticket_str):
    # Convertimos id_ticket_str a uuid
    try:
        id_ticket = uuid.UUID(id_ticket_str)

    except ValueError:
        print("No existe un ticket con ese ID")
        return
    
    # Query con el historia de estados
    SELECT_TICKET_EST = """
        SELECT idTicket, toDate(fecha) as fecha, estado
        FROM ticket_est
        WHERE idTicket = %s
    """

    rows = session.execute(SELECT_TICKET_EST, (id_ticket,))
    # Resultados del query
    print(f"📝 Historial de estados del ticket {id_ticket_str}:")
    for row in rows:
        ticket_est = estadoDict[row.estado]
        print(f"- {row.fecha} | {ticket_est}")
    
# 5. Historial de estado de cuenta de cliente
def historial_client(session, id_client_str):
    # Convertimos id_client_str a uuid
    try:
        id_client = uuid.UUID(id_client_str)

    except ValueError:
        print("No hay ningún cliente con ese ID")
        return

    # Query para el historial de estado de cuenta
    SELECT_CLIENT_CUENTA = """
        SELECT idCliente, toDate(fecha) as fecha, estadoCuenta
        FROM cliente
        WHERE idCliente = %s
    """

    rows = session.execute(SELECT_CLIENT_CUENTA, (id_client,))
    # Resultados del query
    print(f"📝 Historial de estados de cuenta del cliente {id_client_str}:")
    for row in rows:
        client_cuenta = estadoCuentaDict[row.estadocuenta]
        print(f"- {row.fecha} | {client_cuenta}")

# 6. Historial de estado en empresa de agente
def historial_agente(session, id_agente_str):
    # Convertimos id_agente_str a uuid
    try:
        id_agente = uuid.UUID(id_agente_str)

    except ValueError:
        print("No hay ningún agente con ese ID")
        return
    
    # Query para el historial de estado en empresa
    SELECT_AGENTE_ESTADO = """
        SELECT idAgente, toDate(fecha) as fecha, estadoEnEmpresa
        FROM agente
        WHERE idAgente = %s
    """

    rows = session.execute(SELECT_AGENTE_ESTADO, (id_agente,))
    # Resultados del query
    print(f"📝 Historial de estado en empresa de agente {id_agente_str}:")
    for row in rows:
        agente_estado = estadoEmpresaDict[row.estadoenempresa]
        print(f"- {row.fecha} | {agente_estado}")

# 7. Historial de tickets creados en empresa
def historial_empresa(session, id_empresa_str):
    # Convertimos id_empresa_str a uuid
    try:
        id_empresa = uuid.UUID(id_empresa_str)

    except ValueError:
        print("No hay ninguna empresa con ese ID")
        return

    # Query para el historial de tickets en empresa
    SELECT_TICKETS_EMPRESA = """
        SELECT idEmpresa, toDate(fecha) as fecha, idTicket
        FROM empresa
        WHERE idEmpresa = %s
    """

    rows = session.execute(SELECT_TICKETS_EMPRESA, (id_empresa,))
    # Resultados del query
    print(f"📝 Historial de tickets en empresa {id_empresa_str}:")
    for row in rows:
        print(f"- {row.fecha} | {row.idticket}")

# Historial de tickets creados en empresas en x fecha
def historial_empresa_fecha(session, id_empresa_str, fecha):
    # Convertimos id_empresa_str a uuid
    try:
        id_empresa = uuid.UUID(id_empresa_str)

    except ValueError:
        print("No hay ninguna empresa con ese ID")
        return
    
    # Convertir fecha a un datetime
    if(isinstance(fecha, str)):
        fecha = datetime.fromisoformat(fecha)

    # Query para el historial de tickets en empresa 
    SELECT_TICKETS_EMPRESA_POR_FECHA = """
        SELECT idEmpresa, toDate(fecha) as fecha, idTicket
        FROM empresa
        WHERE idEmpresa = %s AND fecha >= minTimeuuid(%s)
    """

    rows = session.execute(SELECT_TICKETS_EMPRESA_POR_FECHA, (id_empresa, fecha))
    # Resultados del query
    print(f"📝 Historial de tickets en empresa {id_empresa_str} desde el {fecha}:")
    for row in rows:
        print(f"- {row.fecha} | {row.idticket}")