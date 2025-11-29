# 1- Importaciones

#!/usr/bin/env python3
import datetime
import json
import pydgraph
import csv
import sys
import io
from .Formatos import print_formatted
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# 2- Definición de esquema

def set_schema(client):
    schema = """
    type Empresa {
        idEmpresa
        nombreEmpresa
        ubicacion
        
        DA_SERVICIO: [Ticket]
        TIENE: [Agente]
        GUARDA: [Ticket]
    }

    type Agente {
        idAgente
        nombreAgente
        
        TRABAJA: Empresa
        SOLUCIONA: [Ticket]
    }

    type Cliente {
        idCliente
        nombreCliente
        
        AFILIADO_A: Empresa
        ABRE: [Ticket]
    }

    type Ticket {
        idTicket
        tipoProblema
        descripcion
        
        SOLUCIONA: Agente
        LE_CORRESPONDE: Cliente
        PERTENECE: Empresa
        ABRE: Cliente
    }

    idEmpresa: string @index(exact) @upsert .
    nombreEmpresa: string @index(term) .
    ubicacion: geo .

    idAgente: string @index(exact) @upsert .
    nombreAgente: string @index(term) .

    idCliente: string @index(exact) @upsert .
    nombreCliente: string @index(term) .

    idTicket: string @index(exact) @upsert .
    tipoProblema: int .
    descripcion: string @index(fulltext) .

    DA_SERVICIO: [uid] @reverse .
    TIENE: [uid] @reverse .
    TRABAJA: uid @reverse .
    SOLUCIONA: [uid] @reverse .
    LE_CORRESPONDE: uid @reverse .
    ABRE: [uid] @reverse .
    PERTENECE: uid @reverse .
    AFILIADO_A: uid @reverse .
    GUARDA: [uid] @reverse .
    """
    op = pydgraph.Operation(schema=schema)
    client.alter(op) 
# ---------------------------------------------------------------------------------------

# 3- Carga de datos
import csv

def create_data(client):
    empresa_uids = {}
    empresas = []

    # 1️ EMPRESAS
    txn = client.txn()
    try:
        with open('data/dgraph/empresas.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                coords = json.loads(row['ubicacion'])
                lat, lon = coords
                empresa = {
                    'uid': f"_:{row['idEmpresa']}",
                    'idEmpresa': row['idEmpresa'],
                    'nombreEmpresa': row['nombreEmpresa'],
                    'ubicacion': {
                        'type': 'Point',
                        'coordinates': [lon, lat]
                    }
                }
                empresas.append(empresa)

        response = txn.mutate(set_obj=empresas, commit_now=True)
        for row in empresas:
            empresa_uids[row['idEmpresa']] = response.uids.get(row['uid'][2:], '')
    finally:
        txn.discard()
    print("👌 Empresas cargadas con éxito en Dgraph.")

    # 2️ AGENTES
    agente_uids = {}
    agentes = []

    txn = client.txn()
    try:
        with open('data/dgraph/agentes.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                agente = {
                    'uid': f"_:{row['idAgente']}",
                    'idAgente': row['idAgente'],
                    'nombreAgente': row['nombreAgente']
                }
                agentes.append(agente)

        response = txn.mutate(set_obj=agentes, commit_now=True)
        for row in agentes:
            agente_uids[row['idAgente']] = response.uids.get(row['uid'][2:], '')
    finally:
        txn.discard()
    print("👌 Agentes cargados con éxito en Dgraph.")

    # 3️ CLIENTES
    cliente_uids = {}
    clientes = []

    txn = client.txn()
    try:
        with open('data/dgraph/clientes.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cliente = {
                    'uid': f"_:{row['idCliente']}",
                    'idCliente': row['idCliente'],
                    'nombreCliente': row['nombreCliente']
                }
                clientes.append(cliente)

        response = txn.mutate(set_obj=clientes, commit_now=True)
        for row in clientes:
            cliente_uids[row['idCliente']] = response.uids.get(row['uid'][2:], '')
    finally:
        txn.discard()
    print("👌 Clientes cargados con éxito en Dgraph.")

    # 4️ TICKETS
    ticket_uids = {}
    tickets = []

    txn = client.txn()
    try:
        with open('data/dgraph/tickets.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ticket = {
                    'uid': f"_:{row['idTicket']}",
                    'idTicket': row['idTicket'],
                    'tipoProblema': int(row['tipoProblema']),
                    'descripcion': row['descripcion']
                }
                tickets.append(ticket)

        response = txn.mutate(set_obj=tickets, commit_now=True)
        for row in tickets:
            ticket_uids[row['idTicket']] = response.uids.get(row['uid'][2:], '')
    finally:
        txn.discard()
    print("👌 Tickets cargados con éxito en Dgraph.")

    # 5️ RELACIONES
    txn = client.txn()
    try:
        all_uids = {**empresa_uids, **agente_uids, **cliente_uids, **ticket_uids}
        with open('data/dgraph/relaciones.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # No toma en cuenta las filas vacías 
                if not row['origen'].strip() or not row['relacion'].strip() or not row['destino'].strip():
                    continue
                origen_id = row['origen'].strip()
                tipo_relacion = row['relacion'].strip().strip('"')
                destino_id = row['destino'].strip()

                origen_uid = all_uids.get(origen_id)
                destino_uid = all_uids.get(destino_id)

                if origen_uid and destino_uid:
                    relacion = {
                        'uid': origen_uid,
                        tipo_relacion: {'uid': destino_uid}
                    }

                    txn.mutate(set_obj=relacion)
                else:
                    print(f"🤦‍♀️ UIDs no encontrados: origen={origen_id}, destino={destino_id}")

        txn.commit()
        print("👌 Todas las relaciones cargadas con éxito.")
    finally:
        txn.discard()
#========================================== QUERYS ===========================================#

def print_json(res):
    print(json.dumps(json.loads(res.json), indent=2, ensure_ascii=False))

# 1. Agentes por empresa

def Agentes_por_empresa(client, id_empresa):
    query = """
    query AgentesPorEmpresa($idEmpresa: string) {
      empresa(func: eq(idEmpresa, $idEmpresa)) {
        idEmpresa
        nombreEmpresa
        TIENE {
          idAgente
          nombreAgente
        }
      }
    }
    """
    variables = {"$idEmpresa": id_empresa}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "agentes_empresa")

# 2. Clientes por empresa

def Clientes_por_empresa(client, id_empresa):
    query = """
    query clientesPorEmpresa($idEmpresa: string) {
      empresa(func: eq(idEmpresa, $idEmpresa)) {
        idEmpresa
        nombreEmpresa
        clientes: ~AFILIADO_A {
          idCliente
          nombreCliente
        }
      }
    }
    """
    variables = {'$idEmpresa': id_empresa}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "clientes_empresa")

# 3. Cliente por ticket

def Cliente_por_ticket(client, idTicket):
    query = """
    query clientePorTicket($idTicket: string) {
      ticket(func: eq(idTicket, $idTicket)) {
        idTicket
        tipoProblema
        descripcion
        ~ABRE {  
          idCliente
          nombreCliente
        }
      }
    }
    """
    variables = {'$idTicket': idTicket}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "clientes_ticket")

# 4. Tickets por empresa
def Tickets_por_empresa(client, id_empresa):
    query = """
    query ticketsPorEmpresa($idEmpresa: string) {
      empresa(func: eq(idEmpresa, $idEmpresa)) {
        nombreEmpresa
        ~PERTENECE {
          idTicket
          tipoProblema
          descripcion
        }
      }
    }
    """
    variables = {'$idEmpresa': id_empresa}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "tickets_empresa")

# 5. Tickets por cliente
def Tickets_por_cliente(client, nombre_cliente):
    query = """
    query ticketsPorCliente($nombreCliente: string) {
      cliente(func: eq(nombreCliente, $nombreCliente)) {
        idCliente
        nombreCliente
        ABRE {
          idTicket
          tipoProblema
          descripcion
        }
      }
    }
    """
    variables = {'$nombreCliente': nombre_cliente}
    res = client.txn(read_only=True).query(query, variables=variables)
    #print_json(res)
    print_formatted(res, "tickets_cliente")

# 6. Agentes por ticket
def Agentes_por_ticket(client, id_ticket):
    query = """
    query agentesPorTicket($idTicket: string) {
      ticket(func: eq(idTicket, $idTicket)) {
        idTicket
         ~SOLUCIONA {
          idAgente
          nombreAgente
        }
      }
    }
    """
    variables = {'$idTicket': id_ticket}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "agente_ticket")

# 7. Tickets de empresa por tipo de problema.
def Tickets_por_empresa_tipo(client, id_empresa,tipo_problema):
    query = """
    query ticketsPorAgenteEmpresaTipo($idEmpresa: string, $tipoProblema: int) {
      empresa(func: eq(idEmpresa, $idEmpresa)) {
        nombreEmpresa
        ~PERTENECE @filter(eq(tipoProblema, $tipoProblema)) {
          idTicket
          tipoProblema
          descripcion
        }
      }
    }
    """
    variables = {'$idEmpresa':id_empresa,'$tipoProblema': tipo_problema}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "tickets_empresa_tipo")

# 8. Tickets por agente por tipo de problema.

def Tickets_por_agente_tipo(client, id_agente,tipo_problema):
    query = """
    query ticketsPorAgenteTipo($idAgente: string, $tipoProblema: int) {
      agente(func: eq(idAgente, $idAgente)) {
        nombreAgente
        SOLUCIONA @filter(eq(tipoProblema, $tipoProblema)) {
          idTicket
          tipoProblema
          descripcion
        }
      }
    }
    """
    variables = {'$idAgente': id_agente,'$tipoProblema': tipo_problema}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "tickets_agente_tipo")


# 9. Ticket por empresa por medio de palabras clave.
def Ticket_por_empresa_palabras(client, empresa_id, palabras_clave):
    query = """
    query ticketsPorEmpresaPalabras($empresa_id: string, $palabras_clave: string) {
      empresa(func: eq(idEmpresa, $empresa_id)) {
        nombreEmpresa
        ~PERTENECE @filter(anyofterms(descripcion, $palabras_clave)) {
          idTicket
          descripcion
          tipoProblema
        }
      }
    }
    """
    variables = {'$empresa_id': empresa_id, '$palabras_clave': palabras_clave}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "tickets_empresa_palabras")

# 10. Búsqueda de Ticket por Agente y Empresa por medio de palabras clave.
def Ticket_por_agente_empresa_palabras(client, empresa_id, agente_id, palabras_clave):
    query = """
    query buscarTicketsAgenteEmpresa($idEmpresa: string, $idAgente: string, $palabras_clave: string) {
      empresa(func: eq(idEmpresa, $idEmpresa)) {
        nombreEmpresa
        TIENE @filter(eq(idAgente, $idAgente)) {
          nombreAgente
          SOLUCIONA @filter(anyofterms(descripcion, $palabras_clave)) {
            idTicket
            descripcion
            tipoProblema
          }
        }
      }
    }
    """
    variables = {'$idEmpresa': empresa_id,'$idAgente': agente_id,'$palabras_clave': palabras_clave}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "tickets_agente_empresa_palabras")

# 11. Dirección de la empresa por medio de su ID.

def Direccion_empresa_por_id(client, idEmpresa):
    query = """
    query ubicacionEmpresa($idEmpresa: string) {
      empresa(func: eq(idEmpresa, $idEmpresa)) {
        nombreEmpresa
        ubicacion {
          type
          coordinates
        }
      }
    }
    """
    variables = {'$idEmpresa': idEmpresa}
    res = client.txn(read_only=True).query(query, variables=variables)
    print_formatted(res, "direccion_empresa")

# 12. BORRAR DATOS
def drop_all(client):
    try:
        op = pydgraph.Operation(drop_all=True)
        client.alter(op)
        print("Se ha eliminado todo el esquema y los datos de Dgraph.")
    except Exception as e:
        print(f"Error al eliminar todo: {e}")

# ==================================== INSERTACIONES ===========================================

# 13. Insertar empresa

def insertar_empresa(client, empresa_data):
    """Inserta una nueva empresa en Dgraph"""
    txn = client.txn()
    try:
        if 'ubicacion' in empresa_data:
            longitud, latitud = empresa_data['ubicacion']
            empresa_data['ubicacion'] = {
                'type': 'Point',
                'coordinates': [longitud, latitud]
            }

        mutation = {
            'uid': f"_:{empresa_data['idEmpresa']}",
            'idEmpresa': str(empresa_data['idEmpresa']),
            'nombreEmpresa': empresa_data['nombreEmpresa'],
            'ubicacion': empresa_data['ubicacion'] 
        }

        print("Mutación enviada a Dgraph:")
        print(json.dumps(mutation, indent=2))

        response = txn.mutate(set_obj=mutation, commit_now=True)
        empresa_uid = response.uids.get(empresa_data['idEmpresa'])

        print(f"Empresa insertada con UID: {empresa_uid}")
        return empresa_uid

    except Exception as e:
        print(f"Error en la inserción de empresa: {e}")
    finally:
        txn.discard()

# 14. Insertar Agente

def insertar_agente(client, agente_data):
    """Inserta un nuevo agente en Dgraph"""

    uid_temp = f"agente_{str(agente_data['idAgente']).replace('-', '')}"

    # 1. Obtener el UID real de la empresa
    query = f"""
    {{
        empresa(func: eq(idEmpresa, "{agente_data['idEmpresa']}")) {{
            uid
        }}
    }}
    """
    response = client.txn(read_only=True).query(query)
    data = json.loads(response.json)
    empresa_uid = data.get("empresa", [{}])[0].get("uid")

    if not empresa_uid:
        raise Exception("No se encontró la empresa en Dgraph con ese idEmpresa.")

    # 2. Insertar el agente
    txn1 = client.txn()
    try:
        mutation = {
            'uid': f"_:{uid_temp}",
            'idAgente': str(agente_data['idAgente']),
            'nombreAgente': agente_data['nombreAgente']
        }

        response = txn1.mutate(set_obj=mutation, commit_now=True)
        agente_uid = response.uids.get(uid_temp)
    finally:
        txn1.discard()

    # 3. Crear la relación
    txn2 = client.txn()
    try:
        relacion = {
            'uid': agente_uid,
            'TRABAJA': {'uid': empresa_uid}
        }
        txn2.mutate(set_obj=relacion, commit_now=True)
    finally:
        txn2.discard()

    print(f"Agente insertado con UID: {agente_uid}")
    return agente_uid


# 15. Insertar Cliente

def insertar_cliente(client, cliente_data):
    """Inserta un nuevo cliente en Dgraph"""

    uid_temp = f"cliente_{str(cliente_data['idCliente']).replace('-', '')}"

    # 1. Obtener el UID real de la empresa
    query = f"""
    {{
        empresa(func: eq(idEmpresa, "{cliente_data['idEmpresa']}")) {{
            uid
        }}
    }}
    """
    response = client.txn(read_only=True).query(query)
    data = json.loads(response.json)
    empresa_uid = data.get("empresa", [{}])[0].get("uid")

    if not empresa_uid:
        raise Exception("No se encontró la empresa con ese idEmpresa en Dgraph.")

    # 2. Insertar el cliente
    txn1 = client.txn()
    try:
        mutation = {
            'uid': f"_:{uid_temp}",
            'idCliente': str(cliente_data['idCliente']),
            'nombreCliente': cliente_data['nombreCliente']
        }

        response = txn1.mutate(set_obj=mutation, commit_now=True)
        cliente_uid = response.uids.get(uid_temp)
    finally:
        txn1.discard()

    # 3. Crear la relación AFILIADO_A
    txn2 = client.txn()
    try:
        relacion = {
            'uid': cliente_uid,
            'AFILIADO_A': {'uid': empresa_uid}
        }
        txn2.mutate(set_obj=relacion, commit_now=True)
    finally:
        txn2.discard()

    print(f"Cliente insertado con UID: {cliente_uid}")
    return cliente_uid


# 16. Insertar Ticket
# 16. Insertar Ticket
def insertar_ticket(client, ticket_data):
    """Inserta un nuevo ticket en Dgraph"""

    id_ticket_str = str(ticket_data['idTicket'])
    id_cliente_str = str(ticket_data['idCliente']) if 'idCliente' in ticket_data and ticket_data['idCliente'] else None
    id_agente_str = str(ticket_data['idAgente']) if 'idAgente' in ticket_data and ticket_data['idAgente'] else None
    id_empresa_str = str(ticket_data['idEmpresa']) if 'idEmpresa' in ticket_data and ticket_data['idEmpresa'] else None

    uid_temp = f"ticket_{id_ticket_str.replace('-', '')}"

    # 1. Insertar ticket
    txn1 = client.txn()
    try:
        mutation = {
            'uid': f"_:{uid_temp}",
            'idTicket': id_ticket_str,
            'tipoProblema': ticket_data['tipo_problema'],
            'descripcion': ticket_data.get('descripcion', '')
        }

        response = txn1.mutate(set_obj=mutation, commit_now=True)
        ticket_uid = response.uids.get(uid_temp)
    finally:
        txn1.discard()

    # 2. Relacionar con cliente, agente y empresa
    relaciones = {}
    if id_cliente_str:
        # Buscar UID real del cliente
        query = f"""{{ q(func: eq(idCliente, "{id_cliente_str}")) {{ uid }} }}"""
        resp = client.txn(read_only=True).query(query)
        data = json.loads(resp.json)
        uid_cliente = data.get("q", [{}])[0].get("uid")
        if uid_cliente:
            relaciones['ABRE'] = {'uid': uid_cliente}

    if id_agente_str:
        query = f"""{{ q(func: eq(idAgente, "{id_agente_str}")) {{ uid }} }}"""
        resp = client.txn(read_only=True).query(query)
        data = json.loads(resp.json)
        uid_agente = data.get("q", [{}])[0].get("uid")
        if uid_agente:
            relaciones['SOLUCIONA'] = {'uid': uid_agente}

    if id_empresa_str:
        query = f"""{{ q(func: eq(idEmpresa, "{id_empresa_str}")) {{ uid }} }}"""
        resp = client.txn(read_only=True).query(query)
        data = json.loads(resp.json)
        uid_empresa = data.get("q", [{}])[0].get("uid")
        if uid_empresa:
            relaciones['PERTENECE'] = {'uid': uid_empresa}

    # Aplicar relaciones si existen
    if relaciones:
        txn2 = client.txn()
        try:
            relacion_mutation = {'uid': ticket_uid, **relaciones}
            txn2.mutate(set_obj=relacion_mutation, commit_now=True)
        finally:
            txn2.discard()

    print(f"Ticket insertado con UID: {ticket_uid}")
    return ticket_uid
