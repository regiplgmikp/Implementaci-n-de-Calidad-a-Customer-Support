import csv
import os
import uuid
from datetime import datetime
from cassandra.util import uuid_from_time
from data_access.db_connection import DBConnection


def _leer_csv_cassandra(filename):
    """Helper para leer archivos CSV de Cassandra."""
    # Ruta relativa a la carpeta scripts/ a la carpeta de CSVs de Cassandra
    base_csv = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/csv/cassandra")
    )
    ruta = f"{base_csv}/{filename}"
    if not os.path.exists(ruta):
        print(f"   ⚠️ CSV {filename} no encontrado en {base_csv}. Saltando carga.")
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _poblar_tabla_cassandra(session, table_name, data, columns, id_keys):
    """Función genérica para insertar datos en una tabla de Cassandra."""
    if not data:
        return

    col_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
    prepared = session.prepare(insert_query)

    for row in data:
        try:
            values = []
            for col in columns:
                value = row.get(col, None)

                # Conversión a UUID
                if col in id_keys and value and value.strip():
                    value = uuid.UUID(value.strip())
                # Conversión de Fecha a TIMEUUID
                elif col == "fecha" and value and value.strip():
                    fecha_datetime = datetime.fromisoformat(
                        value.strip().replace("Z", "")
                    )
                    value = uuid_from_time(fecha_datetime)
                # Conversión a INT si es un campo numérico
                elif (
                    col in ["estado", "prioridad", "estadoEnEmpresa", "estadoCuenta"]
                    and value
                ):
                    value = int(value)

                values.append(value)

            session.execute(prepared, values)
        except Exception as e:
            # Capturamos errores específicos de formato de fila
            print(f"   ❌ Error en fila de {table_name}: {e}. Datos: {row}")

    print(f"   ✅ Cassandra: Tabla {table_name} poblada con {len(data)} registros.")


def poblar_cassandra():
    """Ejecuta la carga masiva de datos históricos en Cassandra."""
    print("--------------------------------------------------")
    print("📚 INICIANDO POBLADO HISTÓRICO DE CASSANDRA...")
    session = DBConnection.get_cassandra_session()

    # 1. EMPRESA
    data_empresa = _leer_csv_cassandra("empresas.csv")
    _poblar_tabla_cassandra(
        session,
        "empresa",
        data_empresa,
        ["idEmpresa", "fecha", "idTicket"],
        ["idEmpresa", "idTicket"],
    )

    # 2. AGENTE
    data_agente = _leer_csv_cassandra("agentes.csv")
    _poblar_tabla_cassandra(
        session,
        "agente",
        data_agente,
        ["idAgente", "fecha", "estadoEnEmpresa"],
        ["idAgente"],
    )

    # 3. CLIENTE
    data_cliente = _leer_csv_cassandra("clientes.csv")
    _poblar_tabla_cassandra(
        session,
        "cliente",
        data_cliente,
        ["idCliente", "fecha", "estadoCuenta"],
        ["idCliente"],
    )

    # 4. HISTORIAL TICKETS (Comentarios, Agente, Estado, Prioridad)
    data_com = _leer_csv_cassandra("tickets_com.csv")
    _poblar_tabla_cassandra(
        session,
        "ticket_com",
        data_com,
        ["idTicket", "fecha", "idAgente", "comentario"],
        ["idTicket", "idAgente"],
    )

    data_age = _leer_csv_cassandra("tickets_age.csv")
    _poblar_tabla_cassandra(
        session,
        "ticket_age",
        data_age,
        ["idTicket", "fecha", "idAgente"],
        ["idTicket", "idAgente"],
    )

    data_est = _leer_csv_cassandra("tickets_est.csv")
    _poblar_tabla_cassandra(
        session, "ticket_est", data_est, ["idTicket", "fecha", "estado"], ["idTicket"]
    )

    data_prio = _leer_csv_cassandra("tickets_prio.csv")
    _poblar_tabla_cassandra(
        session,
        "ticket_prio",
        data_prio,
        ["idTicket", "fecha", "prioridad"],
        ["idTicket"],
    )

    print("--------------------------------------------------")
    print("✅ Poblado histórico de Cassandra finalizado.")


def eliminar_cassandra():
    """Elimina el keyspace completo."""
    session = DBConnection.get_cassandra_session()
    try:
        session.execute("DROP KEYSPACE IF EXISTS cassandra_final")
        print("💥 Keyspace cassandra_final eliminado por completo.")
    except Exception as e:
        print(f"❌ Error al eliminar keyspace: {e}")
