import models.conection as conection
from typing import Type, Union
from .Agente import Agente
from .Empresa import Empresa
from .Cliente import Cliente
from .Ticket import Ticket
from bson import Binary
from uuid import UUID
from models.Utils.validaciones import Validaciones
import pymongo

class MongoModel:
    db = conection.connect_mongodb()

    # Creación de colecciones si no existen
    collections = ['agentes', 'empresas', 'clientes', 'tickets']
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)

    # Creación de índices 
    # Para manejo correcto de indices unicos
    db.agentes.create_index('idAgente', unique=True)
    db.empresas.create_index('idEmpresa', unique=True)
    db.clientes.create_index('idCliente', unique=True)
    db.tickets.create_index('idTicket', unique=True)

    # para consultas:
    # Para Obtener información de agente en base a su nombre o id:
    db.agentes.create_index([("nombre", pymongo.TEXT)], default_language="none")
    db.empresas.create_index([("nombre", pymongo.TEXT)], default_language="none")
    db.clientes.create_index([("nombre", pymongo.TEXT)], default_language="none")
    # Para Mostrar Tickets con estado especifico por entidad
    db.empresas.create_index([('idEmpresa', 1), ('estado', 1)])
    db.agentes.create_index([('idAgente', 1), ('estado', 1)])
    db.clientes.create_index([('idCliente', 1), ('estado', 1)])
    # Para Filtrar tickets de empresa por prioridad
    db.tickets.create_index([('idEmpresa', 1), ('prioridad', 1)])
    # Para Mostrar tickets de una empresa con una antigüedad mayor a “x” fecha
    db.tickets.create_index([('idEmpresa', 1), ('fechaCreacion', 1)])
    # Para Mostrar tickets cerrados en un periodo de tiempo por agente
    db.tickets.create_index([('idAgente', 1), ('fechaCierre', 1)])

    # Para pipelines:
    # Para Mostrar información de clientes y IDs de tickets de una empresa con tickets abiertos a partir de “x” fecha hasta la actualidad
    db.tickets.create_index([('idEmpresa', 1), ('estado', 1), ('fechaCreacion', -1)])
    # Para Obtener la cantidad de tickets que ha cerrado cada agente de una empresa en un periodo de tiempo
    db.tickets.create_index([('idEmpresa', 1), ('estado', 1), ('fechaCierre', -1)])
    # Obtener la cantidad de tickets que ha cerrado un agente de una empresa en un periodo de tiempo
    db.tickets.create_index([('idEmpresa', 1), ('idAgente', 1), ('estado', 1), ('fechaCierre', -1)])

    @classmethod
    def insertar_agente(cls, agente):
        return cls._insertar_documento('agentes', agente, Agente)

    @classmethod
    def obtener_agente_por_id(cls, idAgente: UUID):
        if not isinstance(idAgente, UUID):
            idAgente = UUID(idAgente)
        agente = cls.buscar_documentos('agentes', {'idAgente': idAgente})
        if agente:
            return Agente.crear_desde_dict(agente[0])

    @classmethod
    def obtener_agente_por_nombre(cls, nombreAgente: str):
        agentes = cls.buscar_documentos('agentes', {"$text": {"$search": nombreAgente}})

        # Si se encuentra uno o más agentees, se converten en instancia de Agente y se agregan a lista
        if agentes:
            result = []
            for agente in agentes:
                result.append(Agente.crear_desde_dict(agente))

            return result
        
    @classmethod
    def actualizar_agente(cls, idAgente: UUID, cambios: dict):
        """Actualiza el estado y teléfono de un agente en la base de datos."""
        try:
            collection = cls.db["agentes"]

            # Convertir UUID a Binary
            idAgente_bin = Binary.from_uuid(idAgente)
            
            cambios_filtrados = Validaciones.validar_camposActualizacion(cambios, ["estadoEnEmpresa", "telefono"])
            print("Cambios: ", cambios_filtrados)
            # Actualizar en MongoDB
            resultado = collection.update_one({"idAgente": idAgente_bin}, {"$set": cambios_filtrados})

            if resultado.matched_count == 0:
                raise ValueError(f"No se encontró un agente con ID {idAgente}")

            return cls.obtener_agente_por_id(idAgente)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def insertar_empresa(cls, empresa):
        return cls._insertar_documento('empresas', empresa, Empresa)

    @classmethod
    def obtener_empresa_por_id(cls, idEmpresa: UUID):
        if not isinstance(idEmpresa, UUID):
            idEmpresa = UUID(idEmpresa)

        empresa = cls.buscar_documentos('empresas', {'idEmpresa': idEmpresa, })
        if empresa:
            return Empresa.crear_desde_dict(empresa[0])

    @classmethod
    def obtener_empresa_por_nombre(cls, nombreEmpresa: str):
        empresas = cls.buscar_documentos('empresas', {"$text": {"$search": nombreEmpresa}})

        # Si se encuentra uno o más agentees, se converten en instancia de Agente y se agregan a lista
        if empresas:
            result = []
            for empresa in empresas:
                result.append(Empresa.crear_desde_dict(empresa))

            return result

    @classmethod
    def insertar_cliente(cls, cliente):
        return cls._insertar_documento('clientes', cliente, Cliente)

    @classmethod
    def obtener_cliente_por_id(cls, idCliente: UUID):
        if not isinstance(idCliente, UUID):
            idCliente = UUID(idCliente)
        cliente = cls.buscar_documentos('clientes', {'idCliente': idCliente})
        if cliente:
            return Cliente.crear_desde_dict(cliente[0])
    
    @classmethod
    def obtener_clientes_por_nombre(cls, nombreCliente: str):
        clientes = cls.buscar_documentos('clientes', {"$text": {"$search": nombreCliente}})

        # Si se encuentra uno o más agentees, se converten en instancia de Agente y se agregan a lista
        if clientes:
            result = []
            for cliente in clientes:
                result.append(Cliente.crear_desde_dict(cliente))

            return result

    @classmethod
    def actualizar_cliente(cls, idCliente: UUID, cambios: dict):
        """Actualiza el telefono, correo, estadoCuenta de un cliente en la base de datos."""
        try:
            collection = cls.db["clientes"]

            # Convertir UUID a Binary
            idCliente_bin = Binary.from_uuid(idCliente)
            
            cambios_filtrados = Validaciones.validar_camposActualizacion(cambios, ["telefono", "correo", "estadoCuenta"])
            print("Cambios: ", cambios_filtrados)

            # Actualizar en MongoDB
            resultado = collection.update_one({"idCliente": idCliente_bin}, {"$set": cambios_filtrados})

            if resultado.matched_count == 0:
                raise ValueError(f"No se encontró un cliente con ID {idCliente}")

            return cls.obtener_cliente_por_id(idCliente)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def insertar_ticket(cls, ticket):
        return cls._insertar_documento('tickets', ticket, Ticket)

    @classmethod
    def obtener_ticket_por_id(cls, idTicket: UUID):
        # Retornamos solo el ticket, no una lista
        if not isinstance(idTicket, UUID):
            idTicket = UUID(idTicket)
        ticket = cls.buscar_documentos('tickets', {'idTicket': idTicket})
        if ticket:
            return Ticket.crear_desde_dict(ticket[0])

    @classmethod
    def actualizar_ticket(cls, idTicket: UUID, cambios: dict):
        """Actualiza el fecha de cierre, estado, agente asignado, prioridad de un agente en la base de datos."""
        try:
            collection = cls.db["tickets"]

            # Convertir UUID a Binary
            idTicket_bin = Binary.from_uuid(idTicket)

            cambios_filtrados = Validaciones.validar_camposActualizacion(cambios, ["fechaCierre", "estadoTicket", "idAgente", "prioridad", "comentarios"])
            print("Cambios: ", cambios_filtrados)

            # Actualizar en MongoDB
            resultado = collection.update_one({"idTicket": idTicket_bin}, {"$set": cambios_filtrados})

            if resultado.matched_count == 0:
                raise ValueError(f"No se encontró un ticket con ID {idTicket}")

            return cls.obtener_ticket_por_id(idTicket)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def _insertar_documento(cls, collection_name: str, data: dict, model_class: Type[Union[Agente, Empresa, Cliente, Ticket]]):
        try:
            collection = cls.db[collection_name]
            data = model_class.crear_desde_dict(data)

            # Convertir UUIDs a Binary para MongoDB
            data_dict = data.model_dump(by_alias=True)
            for key, value in data_dict.items():
                if isinstance(value, UUID):
                    data_dict[key] = Binary.from_uuid(value)

            collection.insert_one(data_dict)
            return data # Si hay algún error en la inserción, no se llega a esta linea, solo si todo salio correctamente, se retorna la coleccion creada
        except Exception as e:
            raise e


    @classmethod
    def buscar_documentos(cls, collection_name: str, query: dict, projection: dict = None):
        """ Recibe un nombre de colleción a buscar, el nombre del campo en base al que se va a buscar y el valor que se quiere buscar
            Retorna los documentos encontrados con esas caracteristicas o lista vacía si no encuentra ninguno en la base de datos
        """
        collection = cls.db[collection_name]

        # Si el valor es un UUID, convertirlo a Binary para la consulta
        for key, value in query.items():
            if isinstance(value, UUID):
                query[key] = Binary.from_uuid(value)

        # Se buscan documentos con campos recibidos
        documentos = list(collection.find(query, projection))

        # Convertir todos los campos que sean Binary a UUID
        for documento in documentos:
            for key, value in documento.items():
                if isinstance(value, Binary):
                    documento[key] = UUID(bytes=value)

            # Eliminar el campo '_id' para evitar confusión
            documento.pop('_id', None)

        return documentos

    @classmethod
    def buscar_documentos_complejo(cls, collection_name: str, pipeline: list):
        collection = cls.db[collection_name]

        return list(collection.aggregate(pipeline))
    
    @classmethod
    def eliminar_db(cls):
        """Elimina toda la base de datos en MongoDB."""
        try:
            cls.db.client.drop_database(cls.db.name)
            return f"La base de datos '{cls.db.name}' de Mongo ha sido eliminada correctamente."
        except Exception as e:
            return f"Error al eliminar la base de datos: {e}"