from datetime import datetime
import logging

# Importamos los repositorios (La capa de datos)
# Nota: Si aún no has llenado cassandra_repo o dgraph_repo, mantenlos comentados
# para que no te de error al ejecutar.
from data_access.repositories.mongo_repo import MongoRepository
# from data_access.repositories.cassandra_repo import CassandraRepository
# from data_access.repositories.dgraph_repo import DgraphRepository

class SupportService:
    def __init__(self):
        print("⚙️ Inicializando servicios...")
        # Inicializamos los repositorios
        self.mongo_repo = MongoRepository()
        
        # Pendientes de implementar en siguientes pasos:
        # self.cassandra_repo = CassandraRepository()
        # self.dgraph_repo = DgraphRepository()

    # ----------------------------------------------------------------
    # GESTIÓN DE AGENTES
    # ----------------------------------------------------------------
    def registrar_agente(self, nombre, email, rol):
        """
        Orquesta la creación de un agente.
        1. Guarda los datos maestros en MongoDB.
        2. (Futuro) Inicializa el historial en Cassandra.
        3. (Futuro) Crea el nodo en Dgraph.
        """
        try:
            print(f"   💾 Guardando agente '{nombre}' en MongoDB...")
            
            # 1. Preparar datos para Mongo
            datos_agente = {
                "nombre": nombre,
                "email": email,
                "rol": rol,
                "activo": True,
                "fecha_creacion": datetime.now()
            }
            
            # 2. Llamar al repositorio
            uid = self.mongo_repo.crear_agente(datos_agente)
            
            print(f"   ✅ Agente creado con éxito. ID: {uid}")
            return uid

        except Exception as e:
            print(f"   ❌ Error en registrar_agente: {e}")
            return None

    def obtener_agente(self, identificador, por_id=False):
        try:
            if por_id:
                return self.mongo_repo.obtener_agente_por_id(identificador)
            else:
                return self.mongo_repo.obtener_agente_por_nombre(identificador)
        except Exception as e:
            print(f"Error consultando agente: {e}")
            return None

    # ----------------------------------------------------------------
    # GESTIÓN DE CLIENTES
    # ----------------------------------------------------------------
    def registrar_cliente(self, nombre, email, telefono):
        try:
            datos = {
                "nombre": nombre, 
                "email": email, 
                "telefono": telefono,
                "fecha_registro": datetime.now()
            }
            return self.mongo_repo.crear_cliente(datos)
        except Exception as e:
            print(f"Error creando cliente: {e}")
            return None

    # ----------------------------------------------------------------
    # GESTIÓN DE TICKETS
    # ----------------------------------------------------------------
    def registrar_ticket(self, titulo, descripcion, prioridad, id_cliente):
        try:
            ticket = {
                "titulo": titulo,
                "descripcion": descripcion,
                "prioridad": prioridad,
                "cliente_id": id_cliente,
                "estado": "Abierto",
                "fecha_creacion": datetime.now()
            }
            # Aquí en el futuro agregaremos lógica para asignar agente automáticamente
            return self.mongo_repo.crear_ticket(ticket)
        except Exception as e:
            print(f"Error creando ticket: {e}")
            return None
    
    # ----------------------------------------------------------------
    # UTILIDADES
    # ----------------------------------------------------------------
    def cerrar_conexiones(self):
        # Cerramos las conexiones de forma segura
        from data_access.db_connection import DBConnection
        DBConnection.close_all()