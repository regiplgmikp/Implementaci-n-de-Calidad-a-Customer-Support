from datetime import datetime
from business.services_base import BaseService
from data_access.repositories.mongo_repo import MongoRepository
from data_access.repositories.cassandra_repo import CassandraRepository
from data_access.repositories.dgraph_repo import DgraphRepository
from data_access.db_connection import DBConnection


class SupportService(BaseService):
    """
    Capa de Lógica de Negocio (Fachada).
    Orquesta las interacciones entre Mongo, Cassandra y Dgraph.
    """

    def __init__(self):
        super().__init__()  # Inicializa el logger de BaseService
        self.log_info("⚙️ Inicializando servicios completos (Mongo, Cass, Dgraph)...")
        # Inicializamos los 3 repositorios
        self.mongo_repo = MongoRepository()
        self.cassandra_repo = CassandraRepository()
        self.dgraph_repo = DgraphRepository()

    # ----------------------------------------------------------------
    # GESTIÓN DE AGENTES (Escritura)
    # ----------------------------------------------------------------
    def registrar_agente(self, nombre, email, rol):
        try:
            self.log_info(f"🚀 Iniciando registro de Agente: {nombre}")
            
            # 1. Mongo
            datos_agente = {
                "nombre": nombre, "email": email, "rol": rol,
                "activo": True, "fecha_creacion": datetime.now()
            }
            uid = self.mongo_repo.crear_agente(datos_agente)
            
            # 2. Cassandra
            self.cassandra_repo.registrar_evento(
                uid, "Agente", "CREACION", f"Alta de agente {nombre} con rol {rol}"
            )
            
            # 3. Dgraph
            self.dgraph_repo.crear_nodo_agente(uid, nombre, email)
            return uid
        except Exception as e:
            self.log_error("registrar_agente", e)
            return None

    def obtener_agente(self, identificador, por_id=False):
        if por_id:
            return self.mongo_repo.obtener_agente_por_id(identificador)
        return self.mongo_repo.obtener_agente_por_nombre(identificador)

    # ----------------------------------------------------------------
    # GESTIÓN DE CLIENTES (Escritura)
    # ----------------------------------------------------------------
    def registrar_cliente(self, nombre, email, telefono):
        try:
            self.log_info(f"🚀 Iniciando registro de Cliente: {nombre}")
            datos = {
                "nombre": nombre, "email": email, 
                "telefono": telefono, "fecha_registro": datetime.now()
            }
            uid = self.mongo_repo.crear_cliente(datos)
            
            self.cassandra_repo.registrar_evento(uid, "Cliente", "CREACION", f"Nuevo: {email}")
            self.dgraph_repo.crear_nodo_cliente(uid, nombre)
            return uid
        except Exception as e:
            self.log_error("registrar_cliente", e)
            return None

    # ----------------------------------------------------------------
    # GESTIÓN DE TICKETS (Escritura)
    # ----------------------------------------------------------------
    def registrar_ticket(self, titulo, descripcion, prioridad, id_cliente):
        try:
            self.log_info(f"🚀 Creando Ticket para Cliente {id_cliente}")
            ticket = {
                "titulo": titulo, "descripcion": descripcion,
                "prioridad": prioridad, "cliente_id": id_cliente,
                "estado": 1, "fecha_creacion": datetime.now() # Estado 1 = Abierto
            }
            
            uid_ticket = self.mongo_repo.crear_ticket(ticket)
            
            self.cassandra_repo.registrar_cambio_estado_ticket(
                uid_ticket, "N/A", "Abierto", id_cliente
            )
            
            self.dgraph_repo.crear_nodo_ticket(uid_ticket, titulo, prioridad)
            self.dgraph_repo.relacionar_cliente_ticket(id_cliente, uid_ticket)
            return uid_ticket
        except Exception as e:
            self.log_error("registrar_ticket", e)
            return None

    # ----------------------------------------------------------------
    # CONSULTAS Y LECTURAS (Lo que te faltaba para pasar los tests)
    # ----------------------------------------------------------------
    
    def filtrar_tickets(self, filtros):
        """Consulta tickets en Mongo aplicando filtros"""
        try:
            query = {}
            if 'agente_id' in filtros: query['agente_id'] = filtros['agente_id']
            if 'cliente_id' in filtros: query['cliente_id'] = filtros['cliente_id']
            if 'estado' in filtros: query['estado'] = filtros['estado']
            
            # Nota: Accedemos directo a la colección del repo
            return list(self.mongo_repo.tickets.find(query))
        except Exception as e:
            self.log_error("filtrar_tickets", e)
            return []

    def obtener_ticket_por_id(self, ticket_id):
        """Busca un ticket específico en Mongo"""
        try:
            return self.mongo_repo.tickets.find_one({"id": ticket_id})
        except Exception as e:
            self.log_error("obtener_ticket_por_id", e)
            return None

    def buscar_tickets_avanzado(self, keyword):
        """Búsqueda semántica en Dgraph"""
        try:
            self.log_info(f"🔎 (Dgraph) Buscando: {keyword}")
            return self.dgraph_repo.buscar_tickets_por_keyword(keyword)
        except Exception as e:
            self.log_error("buscar_tickets_avanzado", e)
            return []

    def ver_traza_ticket(self, ticket_id):
        """Historial de cambios en Cassandra"""
        try:
            self.log_info(f"📜 (Cassandra) Historial ticket: {ticket_id}")
            return self.cassandra_repo.obtener_historial_ticket(ticket_id)
        except Exception as e:
            self.log_error("ver_traza_ticket", e)
            return []

    def cerrar_conexiones(self):
        DBConnection.close_all()