import csv
import os
import sys
import json
from data_access.repositories.mongo_repo import MongoRepository
from datetime import datetime

# Configuramos las rutas para encontrar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


def leer_csv_mongo(filename):
    """Lee el CSV principal para crear la entidad maestra."""
    base_csv = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/csv/mongo")
    )
    ruta = f"{base_csv}/{filename}"
    if not os.path.exists(ruta):
        print(f"⚠️ Archivo de origen Mongo no encontrado: {ruta}")
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def poblar_mongo():
    """
    Carga de entidades maestras (Empresa, Agente, Cliente, Ticket) en MongoDB.
    No se usa el SupportService aquí para evitar duplicidad de logs/nodos en las otras BBDD.
    """
    print("\n\n--------------------------------------------------")
    print("💾 INICIANDO POBLADO MAESTRO DE MONGODB...")

    repo = MongoRepository()

    # 1. EMPRESAS
    print("\n🏢 Cargando Empresas...")
    for row in leer_csv_mongo("empresas.csv"):
        datos = {
            "id": row["idEmpresa"],
            "nombre": row["nombre"],
            "correo": row["correo"],
            "telefono": row["telefono"],
            "direccion": row["direccion"],
        }
        repo.crear_empresa(datos)

    # 2. AGENTES
    print("\n🕵️ Cargando Agentes...")
    for row in leer_csv_mongo("agentes.csv"):
        # Parseamos la fecha y el estado/rol del CSV
        fecha_ingreso = datetime.strptime(
            row["fechaIngreso"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S"
        )

        datos = {
            "id": row["idAgente"],
            "nombre": row["nombre"],
            "email": row["correo"],
            "rol": row["rol"],
            "activo": True,
            "fecha_creacion": fecha_ingreso,
        }
        repo.crear_agente(datos)

    # 3. CLIENTES
    print("\n👥 Cargando Clientes...")
    for row in leer_csv_mongo("clientes.csv"):
        datos = {
            "id": row["idCliente"],
            "nombre": row["nombre"],
            "email": row["correo"],
            "telefono": row["telefono"],
            "fecha_registro": datetime.now(),
        }
        repo.crear_cliente(datos)

    # 4. TICKETS
    print("\n🎫 Cargando Tickets...")
    for row in leer_csv_mongo("tickets.csv"):
        comentarios = []
        try:
            # Tu script viejo usaba ast.literal_eval para listas de strings
            if row.get("comentarios"):
                comentarios = json.loads(row["comentarios"].replace("'", '"'))
        except Exception:
            pass  # Si falla el parseo, dejamos vacía

        fecha_cierre = (
            datetime.strptime(row["fechaCierre"], "%Y-%m-%dT%H:%M:%S")
            if row.get("fechaCierre")
            else None
        )

        datos = {
            "id": row["idTicket"],
            "titulo": row.get("titulo", "Ticket Importado"),
            "descripcion": row.get("descripcion", "N/A"),
            "prioridad": int(row["prioridad"]),
            "cliente_id": row["idCliente"],
            "agente_id": row.get("idAgente"),
            "estado": row["estado"],
            "fecha_creacion": datetime.strptime(
                row["fechaCreacion"], "%Y-%m-%dT%H:%M:%S"
            ),
            "fecha_cierre": fecha_cierre,
            "comentarios": comentarios,
        }
        repo.crear_ticket(datos)

    print("\n✅ Poblado Maestro de MongoDB finalizado.")


def eliminar_mongo():
    """Elimina la base de datos de MongoDB."""
    repo = MongoRepository()
    repo.eliminar_db()
