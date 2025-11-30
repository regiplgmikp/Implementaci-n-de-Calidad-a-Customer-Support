import csv
import json
import os
import pydgraph
import sys
from data_access.db_connection import DBConnection
from uuid import UUID

# Configuración de rutas para importar Formatter
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/presentation"))
)

try:
    from formatters import Formatter
except ImportError:

    class Formatter:
        @staticmethod
        def print_formatted(res_json, metodo):
            print(f"--- DGRAPH RESULTADO --- \n{res_json}")


# --- Funciones de Mutación ---


def _ejecutar_mutacion(client, obj_mutar, commit=True):
    """Ejecuta una mutación segura en Dgraph."""
    txn = client.txn()
    try:
        if isinstance(obj_mutar, list):
            txn.mutate(set_obj=obj_mutar, commit_now=commit)
        else:
            txn.mutate(set_obj=obj_mutar, commit_now=commit)
        return txn.commit()
    except Exception as e:
        print(f"   ❌ Error en mutación Dgraph: {e}")
        return None
    finally:
        txn.discard()


def set_schema(client):
    """Define el esquema completo, migrado de tu modelD.py"""
    schema = """
    type Empresa { idEmpresa nombreEmpresa ubicacion TIENE GUARDA }
    type Agente { idAgente nombreAgente TRABAJA SOLUCIONA }
    type Cliente { idCliente nombreCliente AFILIADO_A ABRE }
    type Ticket { idTicket tipoProblema descripcion SOLUCIONA LE_CORRESPONDE PERTENECE ABRE }

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
    
    TIENE: [uid] @reverse .
    TRABAJA: uid @reverse .
    SOLUCIONA: [uid] @reverse .
    ABRE: [uid] @reverse .
    PERTENECE: uid @reverse .
    AFILIADO_A: uid @reverse .
    """
    op = pydgraph.Operation(schema=schema)
    client.alter(op)
    print("   ✅ Dgraph: Esquema configurado.")


def drop_all(client):
    """Elimina todo el esquema y datos de Dgraph."""
    try:
        op = pydgraph.Operation(drop_all=True)
        client.alter(op)
        print("   💥 Dgraph: Esquema y datos eliminados.")
    except Exception as e:
        print(f"   ❌ Error al eliminar Dgraph: {e}")


# --- Funciones de Poblado ---


def poblar_dgraph():
    """Ejecuta la carga masiva de datos en Dgraph."""
    client = DBConnection.get_dgraph_client()
    set_schema(client)  # Inicializar o actualizar esquema

    base_csv = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/csv/dgraph")
    )
    all_uids = {}

    def cargar_entidades(nombre_csv, id_key, type_name):
        """Helper para cargar nodos simples (Empresas, Agentes, Clientes, Tickets)"""
        print(f"   🕸️  Cargando nodos {type_name}...")
        entidades = []
        uid_map = {}
        data = []
        try:
            data = [
                row
                for row in csv.DictReader(
                    open(f"{base_csv}/{nombre_csv}", "r", encoding="utf-8")
                )
            ]
        except FileNotFoundError:
            print(f"   ⚠️ CSV {nombre_csv} no encontrado. Saltando.")
            return {}

        for row in data:
            # Creamos la estructura de mutación
            mutation = {
                "uid": f"_:{row[id_key]}",
                id_key: row[id_key],
                "dgraph.type": type_name,
            }

            # Lógica especial para Empresa (Ubicación)
            if type_name == "Empresa" and "ubicacion" in row and row["ubicacion"]:
                # Asumimos que 'ubicacion' es un string JSON como en tu populate.py
                try:
                    coords = json.loads(row["ubicacion"])
                    mutation["ubicacion"] = {"type": "Point", "coordinates": coords}
                except json.JSONDecodeError:
                    print(f"   ⚠️ Error de JSON en ubicación para {row[id_key]}")

            # Lógica especial para Agente/Cliente/Ticket (campos específicos)
            if type_name == "Agente":
                mutation["nombreAgente"] = row["nombreAgente"]
            elif type_name == "Cliente":
                mutation["nombreCliente"] = row["nombreCliente"]
            elif type_name == "Ticket":
                mutation["tipoProblema"] = int(row["tipoProblema"])
                mutation["descripcion"] = row["descripcion"]

            entidades.append(mutation)

        response = _ejecutar_mutacion(client, entidades)

        # Mapeamos los IDs externos a los UIDs internos de Dgraph
        if response and response.uids:
            for row in data:
                # Usamos el valor del ID externo (UUID) para mapear al UID interno de Dgraph
                uid_map[row[id_key]] = response.uids.get(row[id_key], "")

        print(f"   ✅ Dgraph: {type_name} cargados: {len(data)}")
        return uid_map

    # FASE 1: Carga de Nodos
    uids_empresa = cargar_entidades("empresas.csv", "idEmpresa", "Empresa")
    uids_agente = cargar_entidades("agentes.csv", "idAgente", "Agente")
    uids_cliente = cargar_entidades("clientes.csv", "idCliente", "Cliente")
    uids_ticket = cargar_entidades("tickets.csv", "idTicket", "Ticket")

    # Consolidar todos los UIDs mapeados
    all_uids = {**uids_empresa, **uids_agente, **uids_cliente, **uids_ticket}

    # FASE 2: Carga de Relaciones
    print("\n   🕸️  Cargando Relaciones (relaciones.csv)...")
    relaciones_nquads = []

    try:
        relaciones_data = [
            row
            for row in csv.DictReader(
                open(f"{base_csv}/relaciones.csv", "r", encoding="utf-8")
            )
        ]
    except FileNotFoundError:
        print("   ⚠️ CSV relaciones.csv no encontrado. Saltando relaciones.")
        return

    for row in relaciones_data:
        origen_id = row["origen"].strip()
        tipo_relacion = row["relacion"].strip()
        destino_id = row["destino"].strip()

        origen_uid = all_uids.get(origen_id)
        destino_uid = all_uids.get(destino_id)

        if origen_uid and destino_uid:
            relacion = {"uid": origen_uid, tipo_relacion: {"uid": destino_uid}}
            relaciones_nquads.append(relacion)
        else:
            print(
                f"   🤷‍♀️ Relación omitida (UIDs no encontrados): {origen_id} -> {destino_id}"
            )

    _ejecutar_mutacion(client, relaciones_nquads)
    print(f"   ✅ Dgraph: Relaciones cargadas: {len(relaciones_data)}")
