import uuid
from datetime import datetime

# Importamos la clase para la conexión
from data_access.db_connection import DBConnection


class MongoRepository:
    def __init__(self):
        # En el constructor, "enchufamos" el repositorio a la base de datos
        self.db = DBConnection.get_mongo_db()
        # Definimos las colecciones que vamos a usar
        self.agents = self.db["agents"]
        self.clients = self.db["clients"]
        self.tickets = self.db["tickets"]
        self.companies = self.db["companies"]

    # ---------------------------------------------------------
    # AGENTES
    # ---------------------------------------------------------
    def crear_agente(self, datos_agente):
        """
        Guarda un diccionario de agente en MongoDB.
        Retorna el ID del agente creado.
        """
        # Generamos ID si no viene (Mejora de Integridad de Datos)
        if "id" not in datos_agente:
            datos_agente["id"] = str(uuid.uuid4())

        # Insertamos
        self.agents.insert_one(datos_agente)
        return datos_agente["id"]

    def obtener_agente_por_nombre(self, nombre):
        """Busca un agente por nombre (insensible a mayúsculas)"""
        return self.agents.find_one(
            {"nombre": {"$regex": f"^{nombre}$", "$options": "i"}}
        )

    def obtener_agente_por_id(self, uid):
        return self.agents.find_one({"id": uid})

    # ---------------------------------------------------------
    # CLIENTES (Ejemplo base)
    # ---------------------------------------------------------
    def crear_cliente(self, datos_cliente):
        if "id" not in datos_cliente:
            datos_cliente["id"] = str(uuid.uuid4())
        self.clients.insert_one(datos_cliente)
        return datos_cliente["id"]

    # ---------------------------------------------------------
    # TICKETS (Consultas Analíticas - Requerimiento del Proyecto)
    # ---------------------------------------------------------
    def crear_ticket(self, datos_ticket):
        if "id" not in datos_ticket:
            datos_ticket["id"] = str(uuid.uuid4())
        # Aseguramos fecha de creación
        if "fecha_creacion" not in datos_ticket:
            datos_ticket["fecha_creacion"] = datetime.now()

        self.tickets.insert_one(datos_ticket)
        return datos_ticket["id"]

    def obtener_tickets_por_estado_y_entidad(
        self, entidad_campo, entidad_valor, estado
    ):
        """
        Ejemplo: Traer tickets 'Cerrados' del Agente 'Juan'
        entidad_campo: 'agente_id' o 'empresa_id'
        """
        query = {entidad_campo: entidad_valor, "estado": estado}
        return list(self.tickets.find(query))

    # ---------------------------------------------------------
    # EMPRESAS
    # ---------------------------------------------------------
    def crear_empresa(self, datos_empresa):
        if "id" not in datos_empresa:
            datos_empresa["id"] = str(uuid.uuid4())
        self.companies.insert_one(datos_empresa)
        return datos_empresa["id"]
