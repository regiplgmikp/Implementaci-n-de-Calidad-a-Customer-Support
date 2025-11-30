import os
import logging
import pydgraph
from pymongo import MongoClient
from cassandra.cluster import Cluster

class DBConnection:
    """
    Clase centralizada para manejar las conexiones a las 3 bases de datos.
    Patrón Singleton: Garantiza que solo exista una instancia de conexión activa.
    """
    _dgraph_client = None
    _cassandra_session = None
    _mongo_client = None
    _mongo_db = None

    # ---------------------------------------------------------
    # MONGODB
    # ---------------------------------------------------------
    @staticmethod
    def get_mongo_db():
        if DBConnection._mongo_db is None:
            try:
                # Ajusta el host y puerto si es necesario (ej. 'localhost', 27017)
                host = os.getenv('MONGO_HOST', 'localhost')
                port = int(os.getenv('MONGO_PORT', 27017))
                
                print(f"🔌 Conectando a MongoDB en {host}:{port}...")
                DBConnection._mongo_client = MongoClient(host, port)
                
                # Nombre de la base de datos
                db_name = os.getenv('MONGO_DB_NAME', 'customer_support_db')
                DBConnection._mongo_db = DBConnection._mongo_client[db_name]
                print("✅ Conexión a MongoDB exitosa.")
            except Exception as e:
                print(f"❌ Error conectando a MongoDB: {e}")
                raise
        return DBConnection._mongo_db

    # ---------------------------------------------------------
    # DGRAPH
    # ---------------------------------------------------------
    @staticmethod
    def get_dgraph_client():
        if DBConnection._dgraph_client is None:
            try:
                # Ajusta el host y puerto de Dgraph (ej. 'localhost:9080')
                dgraph_url = os.getenv('DGRAPH_URL', 'localhost:9080')
                
                print(f"🔌 Conectando a Dgraph en {dgraph_url}...")
                client_stub = pydgraph.DgraphClientStub(dgraph_url)
                DBConnection._dgraph_client = pydgraph.DgraphClient(client_stub)
                print("✅ Conexión a Dgraph exitosa.")
            except Exception as e:
                print(f"❌ Error conectando a Dgraph: {e}")
                raise
        return DBConnection._dgraph_client

    # ---------------------------------------------------------
    # CASSANDRA
    # ---------------------------------------------------------
    @staticmethod
    def get_cassandra_session():
        if DBConnection._cassandra_session is None:
            try:
                # Configurar logs para Cassandra (para evitar ruido en consola)
                log = logging.getLogger()
                log.setLevel(logging.ERROR) # Solo mostrar errores graves

                host = os.getenv('CASSANDRA_HOST', '127.0.0.1')
                port = int(os.getenv('CASSANDRA_PORT', 9042))
                
                print(f"🔌 Conectando a Cassandra en {host}:{port}...")
                cluster = Cluster(contact_points=[host], port=port)
                DBConnection._cassandra_session = cluster.connect()
                
                # Configurar Keyspace
                keyspace = os.getenv('CASSANDRA_KEYSPACE', 'cassandra_final')
                # Configuración simple para desarrollo
                replication = "{'class': 'SimpleStrategy', 'replication_factor': 1}"
                
                # Crear keyspace si no existe (importante para evitar errores en primera ejecución)
                DBConnection._cassandra_session.execute(f"""
                    CREATE KEYSPACE IF NOT EXISTS {keyspace}
                    WITH replication = {replication}
                """)
                DBConnection._cassandra_session.set_keyspace(keyspace)
                print("✅ Conexión a Cassandra exitosa.")
                
            except Exception as e:
                print(f"❌ Error conectando a Cassandra: {e}")
                raise

        return DBConnection._cassandra_session

    @staticmethod
    def close_all():
        """Cierra todas las conexiones activas limpiamente."""
        print("\n🔒 Cerrando conexiones...")
        if DBConnection._mongo_client:
            DBConnection._mongo_client.close()
        if DBConnection._cassandra_session:
            DBConnection._cassandra_session.cluster.shutdown()
        # Dgraph no requiere cierre explícito del cliente en pydgraph simple
        print("✅ Conexiones cerradas.")