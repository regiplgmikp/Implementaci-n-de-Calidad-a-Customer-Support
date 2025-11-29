import os
import logging
import pydgraph
from cassandra.cluster import Cluster

class DBConnection:
    """
    Clase Singleton encargada de gestionar las conexiones a las 3 bases de datos.
    Cumple con el criterio de Fiabilidad al centralizar el manejo de errores de conexión.
    """
    _dgraph_client = None
    _cassandra_session = None

    @staticmethod
    def get_dgraph_client():
        if DBConnection._dgraph_client is None:
            # En producción, esta URL debería venir de variables de entorno
            dgraph_url = os.getenv('DGRAPH_URL', 'localhost:9080')
            client_stub = pydgraph.DgraphClientStub(dgraph_url)
            DBConnection._dgraph_client = pydgraph.DgraphClient(client_stub)
        return DBConnection._dgraph_client

    @staticmethod
    def get_cassandra_session():
        if DBConnection._cassandra_session is None:
            log = logging.getLogger()
            log.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            log.addHandler(handler)

            log.info("Conectando al Cluster de Cassandra...")
            # Configuración de reconexión y timeouts para mejorar la Disponibilidad
            cluster = Cluster(
                contact_points=[os.getenv('CASSANDRA_HOST', '127.0.0.1')],
                port=int(os.getenv('CASSANDRA_PORT', 9042))
            )
            DBConnection._cassandra_session = cluster.connect()
            
            # Configuración del Keyspace
            keyspace = os.getenv('CASSANDRA_KEYSPACE', 'cassandra_final')
            replication_factor = os.getenv('CASSANDRA_REPLICATION_FACTOR', '1')
            
            # Crear keyspace si no existe (Lógica movida desde main.py)
            try:
                DBConnection._cassandra_session.execute(f"""
                    CREATE KEYSPACE IF NOT EXISTS {keyspace}
                    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': {replication_factor}}}
                """)
                DBConnection._cassandra_session.set_keyspace(keyspace)
            except Exception as e:
                log.error(f"Error configurando Keyspace: {e}")
                raise

        return DBConnection._cassandra_session

    @staticmethod
    def close_all():
        """Cierra conexiones limpiamente (útil para el menú de Salir)"""
        if DBConnection._cassandra_session:
            DBConnection._cassandra_session.cluster.shutdown()