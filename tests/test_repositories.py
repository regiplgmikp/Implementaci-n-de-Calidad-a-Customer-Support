import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# -------------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS (Vital para encontrar los módulos)
# -------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# -------------------------------------------------------------------------
# MOCKS GLOBALES (Para evitar errores de importación de drivers)
# -------------------------------------------------------------------------
# Simulamos las librerías externas para que no fallen si no están instaladas o configuradas
sys.modules["cassandra"] = MagicMock()
sys.modules["cassandra.cluster"] = MagicMock()
sys.modules["pydgraph"] = MagicMock()
sys.modules["pymongo"] = MagicMock()

# Ahora importamos los repositorios
from data_access.repositories.mongo_repo import MongoRepository  # noqa: E402
from data_access.repositories.cassandra_repo import CassandraRepository  # noqa: E402
from data_access.repositories.dgraph_repo import DgraphRepository  # noqa: E402


class TestMongoRepository:
    """Pruebas unitarias para el repositorio de MongoDB"""

    @pytest.fixture
    def repo(self):
        with patch('data_access.db_connection.DBConnection.get_mongo_db') as mock_db:
            # Simulamos las colecciones
            mock_db.return_value = MagicMock()
            repo = MongoRepository()
            # Asignamos mocks específicos a las colecciones internas
            repo.agents = MagicMock()
            repo.clients = MagicMock()
            repo.tickets = MagicMock()
            return repo

    def test_crear_agente_llama_insert(self, repo):
        # Datos de prueba
        datos = {"nombre": "Test Agent", "email": "test@mail.com"}

        # Ejecutar método
        uid = repo.crear_agente(datos)

        # Validar que se generó un ID
        assert uid is not None
        # Validar que se llamó a insert_one en la colección correcta
        repo.agents.insert_one.assert_called_once()
        # Validar que el objeto insertado contiene los datos
        args, _ = repo.agents.insert_one.call_args
        assert args[0]['nombre'] == "Test Agent"

    def test_obtener_agente_por_nombre(self, repo):
        # Configuramos el mock para que devuelva un resultado simulado
        repo.agents.find_one.return_value = {"nombre": "Juan", "rol": "Admin"}

        resultado = repo.obtener_agente_por_nombre("Juan")

        assert resultado['nombre'] == "Juan"
        repo.agents.find_one.assert_called_once()


class TestCassandraRepository:
    """Pruebas unitarias para el repositorio de Cassandra"""

    @pytest.fixture
    def repo(self):
        with patch('data_access.db_connection.DBConnection.get_cassandra_session') as mock_session:
            # El mock devuelve una sesión falsa
            mock_session.return_value = MagicMock()
            repo = CassandraRepository()
            # Mockeamos la sesión interna del repo
            repo.session = MagicMock()
            return repo

    def test_registrar_evento(self, repo):
        # Ejecutar
        repo.registrar_evento("uid-123", "Agente", "CREACION", "Test desc")

        # Validar que se ejecutó la query CQL
        repo.session.execute.assert_called()
        args, _ = repo.session.execute.call_args
        query_enviada = args[0]
        # Verificar que la query contiene la tabla correcta
        assert "INSERT INTO historial_general" in query_enviada


class TestDgraphRepository:
    """Pruebas unitarias para el repositorio de Dgraph"""

    @pytest.fixture
    def repo(self):
        with patch('data_access.db_connection.DBConnection.get_dgraph_client') as mock_client:
            mock_client.return_value = MagicMock()
            repo = DgraphRepository()
            repo.client = MagicMock()
            return repo

    def test_crear_nodo_agente(self, repo):
        # Simulamos la transacción
        mock_txn = MagicMock()
        repo.client.txn.return_value = mock_txn

        # Ejecutar
        repo.crear_nodo_agente("uid-123", "Bond", "007@mi6.uk")

        # Validar que se creó una mutación
        mock_txn.mutate.assert_called_once()
        # Validar que se hizo commit
        # Nota: Dependiendo de tu imp. puede ser commit_now=True en mutate o txn.commit()
        # En tu código usas commit_now=True dentro de mutate
        args, kwargs = mock_txn.mutate.call_args
        assert kwargs.get('commit_now') is True
