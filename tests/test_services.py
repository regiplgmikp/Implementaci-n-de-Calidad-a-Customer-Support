import sys
import os
from unittest.mock import MagicMock

# -------------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# -------------------------------------------------------------------------
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if src_path not in sys.path:
    sys.path.insert(0, src_path)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# -------------------------------------------------------------------------
# MOCKS GLOBALES
# -------------------------------------------------------------------------
sys.modules["cassandra"] = MagicMock()
sys.modules["cassandra.cluster"] = MagicMock()
sys.modules["pydgraph"] = MagicMock()
sys.modules["pymongo"] = MagicMock()

import pytest
from business.support_service import SupportService  # noqa: E402


@pytest.fixture
def service_mock():
    """Fixture que crea el servicio con repositorios simulados"""
    service = SupportService()
    service.mongo_repo = MagicMock()
    service.cassandra_repo = MagicMock()
    service.dgraph_repo = MagicMock()

    # Mockeamos también las colecciones internas de Mongo para lecturas directas
    service.mongo_repo.tickets = MagicMock()

    return service

# -------------------------------------------------------------------------
# PRUEBAS DE ESCRITURA (REGISTROS) - YA LAS TENÍAS
# -------------------------------------------------------------------------


def test_registrar_agente_exitoso(service_mock):
    service_mock.mongo_repo.crear_agente.return_value = '123-abc'
    uid = service_mock.registrar_agente("Agente 007", "bond@mi6.com", "Soporte")

    assert uid == '123-abc'
    service_mock.mongo_repo.crear_agente.assert_called_once()
    service_mock.cassandra_repo.registrar_evento.assert_called_once()
    service_mock.dgraph_repo.crear_nodo_agente.assert_called_once()


def test_registrar_agente_fallo_mongo(service_mock):
    service_mock.mongo_repo.crear_agente.side_effect = Exception("Error DB")
    uid = service_mock.registrar_agente("Agente Fallido", "error@test.com", "Admin")
    assert uid is None


def test_registrar_cliente_valido(service_mock):
    service_mock.mongo_repo.crear_cliente.return_value = 'cli-999'
    uid = service_mock.registrar_cliente("Cliente Feliz", "c@test.com", "555-1234")
    assert uid == 'cli-999'


def test_registrar_ticket_completo(service_mock):
    service_mock.mongo_repo.crear_ticket.return_value = 'ticket-777'

    uid = service_mock.registrar_ticket("Wifi Lento", "No carga", 1, "cli-999")

    assert uid == 'ticket-777'
    service_mock.cassandra_repo.registrar_cambio_estado_ticket.assert_called_once()
    service_mock.dgraph_repo.relacionar_cliente_ticket.assert_called_once()


# -------------------------------------------------------------------------
# NUEVAS PRUEBAS DE LECTURA (PARA SUBIR COBERTURA > 80%)
# -------------------------------------------------------------------------

def test_filtrar_tickets_mongo(service_mock):
    """Prueba la consulta de tickets con filtros en MongoDB"""
    # 1. Preparamos datos falsos que devolvería Mongo
    mock_tickets = [{"id": "t1", "estado": 1}, {"id": "t2", "estado": 1}]
    # Configuramos el mock para devolver una lista al llamar a .find()
    service_mock.mongo_repo.tickets.find.return_value = mock_tickets

    # 2. Ejecutamos
    filtros = {'estado': 1}
    resultado = service_mock.filtrar_tickets(filtros)

    # 3. Validamos
    assert len(resultado) == 2
    service_mock.mongo_repo.tickets.find.assert_called_once_with({'estado': 1})


def test_filtrar_tickets_error(service_mock):
    """Prueba que el sistema no crashee si Mongo falla al leer"""
    service_mock.mongo_repo.tickets.find.side_effect = Exception("Conexión perdida")
    resultado = service_mock.filtrar_tickets({})
    # Debe retornar lista vacía, no crashear
    assert resultado == []


def test_buscar_tickets_avanzado_dgraph(service_mock):
    """Prueba la búsqueda fulltext en Dgraph"""
    mock_res = [{"idTicket": "t1", "descripcion": "wifi lento"}]
    service_mock.dgraph_repo.buscar_tickets_por_keyword.return_value = mock_res

    resultado = service_mock.buscar_tickets_avanzado("wifi")

    assert len(resultado) == 1
    service_mock.dgraph_repo.buscar_tickets_por_keyword.assert_called_once_with("wifi")


def test_ver_traza_ticket_cassandra(service_mock):
    """Prueba la consulta de historial en Cassandra"""
    mock_hist = [MagicMock(estado_ant="A", estado_new="B")]
    service_mock.cassandra_repo.obtener_historial_ticket.return_value = mock_hist

    resultado = service_mock.ver_traza_ticket("ticket-777")

    assert len(resultado) == 1
    service_mock.cassandra_repo.obtener_historial_ticket.assert_called_once_with("ticket-777")


def test_obtener_ticket_por_id(service_mock):
    service_mock.mongo_repo.tickets.find_one.return_value = {"id": "t1"}
    res = service_mock.obtener_ticket_por_id("t1")
    assert res["id"] == "t1"
