from datetime import datetime

# Importamos los repositorios (La capa de datos)
from data_access.repositories.mongo_repo import MongoRepository
from data_access.repositories.cassandra_repo import CassandraRepository
from data_access.repositories.dgraph_repo import DgraphRepository


class SupportService:
    def __init__(self):
        # Mensaje para confirmar que se cargó la versión correcta
        print("⚙️ Inicializando servicios completos (Mongo, Cass, Dgraph)...")
        # Inicializamos los 3 repositorios
        self.mongo_repo = MongoRepository()
        self.cassandra_repo = CassandraRepository()
        self.dgraph_repo = DgraphRepository()

    # ----------------------------------------------------------------
    # GESTIÓN DE AGENTES
    # ----------------------------------------------------------------
    def registrar_agente(self, nombre, email, rol):
        """
        Flujo Completo:
        1. Mongo: Datos perfil.
        2. Cassandra: Log de 'Alta de Agente'.
        3. Dgraph: Nodo Agente para relaciones.
        """
        try:
            print(f"\n🚀 Iniciando registro de Agente: {nombre}")

            # 1. MongoDB
            datos_agente = {
                "nombre": nombre, "email": email, "rol": rol,
                "activo": True, "fecha_creacion": datetime.now()
            }
            uid = self.mongo_repo.crear_agente(datos_agente)
            print(f"   ✅ MongoDB: ID {uid} generado.")

            # 2. Cassandra (Historial)
            self.cassandra_repo.registrar_evento(
                entidad_id=uid, tipo_entidad="Agente",
                accion="CREACION",
                descripcion=f"Alta de agente {nombre} con rol {rol}"
            )

            # 3. Dgraph (Grafo)
            self.dgraph_repo.crear_nodo_agente(uid, nombre, email)

            return uid

        except Exception as e:
            print(f"   ❌ Error CRÍTICO en registrar_agente: {e}")
            return None

    def obtener_agente(self, identificador, por_id=False):
        # Lectura rápida solo desde Mongo
        if por_id:
            return self.mongo_repo.obtener_agente_por_id(identificador)
        return self.mongo_repo.obtener_agente_por_nombre(identificador)

    # ----------------------------------------------------------------
    # GESTIÓN DE CLIENTES
    # ----------------------------------------------------------------
    def registrar_cliente(self, nombre, email, telefono):
        try:
            print(f"\n🚀 Iniciando registro de Cliente: {nombre}")
            datos = {
                "nombre": nombre, "email": email,
                "telefono": telefono, "fecha_registro": datetime.now()
            }
            # 1. Mongo
            uid = self.mongo_repo.crear_cliente(datos)

            # 2. Cassandra
            self.cassandra_repo.registrar_evento(
                uid, "Cliente", "CREACION", f"Nuevo cliente: {email}"
            )

            # 3. Dgraph
            self.dgraph_repo.crear_nodo_cliente(uid, nombre)

            print("   ✅ Cliente registrado exitosamente en 3 BBDD.")
            return uid
        except Exception as e:
            print(f"   ❌ Error creando cliente: {e}")
            return None

    # ----------------------------------------------------------------
    # GESTIÓN DE TICKETS
    # ----------------------------------------------------------------
    def registrar_ticket(self, titulo, descripcion, prioridad, id_cliente):
        try:
            print(f"\n🚀 Creando Ticket para Cliente {id_cliente}")
            ticket = {
                "titulo": titulo, "descripcion": descripcion,
                "prioridad": prioridad, "cliente_id": id_cliente,
                "estado": "Abierto", "fecha_creacion": datetime.now()
            }

            # 1. Mongo
            uid_ticket = self.mongo_repo.crear_ticket(ticket)

            # 2. Cassandra (Log específico de tickets)
            self.cassandra_repo.registrar_cambio_estado_ticket(
                uid_ticket, "N/A", "Abierto", id_cliente
            )

            # 3. Dgraph (Relación Cliente -> Ticket)
            self.dgraph_repo.crear_nodo_ticket(uid_ticket, titulo, prioridad)
            self.dgraph_repo.relacionar_cliente_ticket(id_cliente, uid_ticket)

            print("   ✅ Ticket creado y relacionado.")
            return uid_ticket

        except Exception as e:
            print(f"   ❌ Error creando ticket: {e}")
            return None

    def cerrar_conexiones(self):
        from data_access.db_connection import DBConnection
        DBConnection.close_all()
