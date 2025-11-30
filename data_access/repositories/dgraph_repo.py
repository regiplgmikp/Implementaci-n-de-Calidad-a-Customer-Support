import json
import pydgraph
from data_access.db_connection import DBConnection

class DgraphRepository:
    def __init__(self):
        self.client = DBConnection.get_dgraph_client()

    def _ejecutar_mutacion(self, nquads):
        """Helper para ejecutar transacciones en Dgraph"""
        txn = self.client.txn()
        try:
            mutation = pydgraph.Mutation(set_nquads=nquads)
            txn.mutate(mutation=mutation, commit_now=True)
            print("   (Dgraph) 🕸️  Nodo/Relación creado.")
        except Exception as e:
            print(f"   (Dgraph) ❌ Error en mutación: {e}")
        finally:
            txn.discard()

    def crear_nodo_agente(self, uid, nombre, email):
        """Crea el nodo del agente para futuras relaciones"""
        # En Dgraph usamos el mismo UUID que en Mongo para mantener integridad
        nquads = f"""
        <_{uid}> <tipo> "Agente" .
        <_{uid}> <nombre> "{nombre}" .
        <_{uid}> <email> "{email}" .
        <_{uid}> <dgraph.type> "Agente" .
        """
        self._ejecutar_mutacion(nquads)

    def crear_nodo_cliente(self, uid, nombre):
        nquads = f"""
        <_{uid}> <tipo> "Cliente" .
        <_{uid}> <nombre> "{nombre}" .
        <_{uid}> <dgraph.type> "Cliente" .
        """
        self._ejecutar_mutacion(nquads)

    def crear_nodo_ticket(self, uid, titulo, prioridad):
        nquads = f"""
        <_{uid}> <tipo> "Ticket" .
        <_{uid}> <titulo> "{titulo}" .
        <_{uid}> <prioridad> "{prioridad}" .
        <_{uid}> <dgraph.type> "Ticket" .
        """
        self._ejecutar_mutacion(nquads)

    def relacionar_cliente_ticket(self, id_cliente, id_ticket):
        """Crea la arista: Cliente -[creo_ticket]-> Ticket"""
        nquads = f"""
        <_{id_cliente}> <creo_ticket> <_{id_ticket}> .
        """
        self._ejecutar_mutacion(nquads)