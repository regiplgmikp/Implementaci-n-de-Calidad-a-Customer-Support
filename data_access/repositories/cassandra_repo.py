from datetime import datetime
import uuid
from data_access.db_connection import DBConnection
class CassandraRepository:
    def __init__(self):
        self.session = DBConnection.get_cassandra_session()
        self.crear_tablas()

    def crear_tablas(self):
        """Inicializa las tablas de historial si no existen"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS historial_general (
                id_evento UUID PRIMARY KEY,
                entidad_id text,
                tipo_entidad text,
                accion text,
                descripcion text,
                fecha timestamp
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS historial_tickets (
                ticket_id text,
                fecha timestamp,
                estado_anterior text,
                estado_nuevo text,
                usuario_id text,
                PRIMARY KEY (ticket_id, fecha)
            ) WITH CLUSTERING ORDER BY (fecha DESC)
            """
        ]
        for q in queries:
            try:
                self.session.execute(q)
            except Exception as e:
                print(f"⚠️ Error inicializando tabla Cassandra: {e}")

    def registrar_evento(self, entidad_id, tipo_entidad, accion, descripcion):
        """Registra cualquier cambio en el sistema (Auditoría General)"""
        query = """
        INSERT INTO historial_general (id_evento, entidad_id, tipo_entidad, accion, descripcion, fecha)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            self.session.execute(query, (
                uuid.uuid4(), 
                str(entidad_id), 
                tipo_entidad, 
                accion, 
                descripcion, 
                datetime.now()
            ))
            print("   (Cassandra) 📜 Evento registrado.")
        except Exception as e:
            print(f"   (Cassandra) ❌ Error registrando evento: {e}")

    def registrar_cambio_estado_ticket(self, ticket_id, est_ant, est_nuevo, user_id):
        """Historial específico para cambios de estado de tickets"""
        query = """
        INSERT INTO historial_tickets (ticket_id, fecha, estado_anterior, estado_nuevo, usuario_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.session.execute(query, (str(ticket_id), datetime.now(), est_ant, est_nuevo, str(user_id)))
        except Exception as e:
            print(f"   (Cassandra) ❌ Error registrando cambio de ticket: {e}")
