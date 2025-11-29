import re
from uuid import UUID
from datetime import datetime
from models.Utils.regularExpresions import (
    nombre_regex,
    correo_regex,
    telefono_regex,
    #para dgraph
    ubicacion_regex
)
from models.Utils.dictionaries import (
    estadoEnEmpresa as estadoEnEmpresaDict,
    estadoCuenta as estadoCuentaDict,
    estado as estadoTicketDict,
    prioridad as prioridadTicketDict,
    tipoProblema
)

def solicitar_input(mensaje, validacion_func=None, canBeNone=False):
    """Solicita un input al usuario y lo valida si es necesario, si se establece como True la variable
    canBeNone, significa que se acepta retornar vacio, sino, se llama a la función de validación, aún con valor vacio y
    esta función de validación se encargará de manejar el valor vacio
    """
    while True:
        valor = input(mensaje)
        if canBeNone and not valor:
            return None
        if validacion_func:
            try:
                return validacion_func(valor)
            except ValueError as e:
                print(f"\tError: {e}")
        else:
            return valor

class Validaciones:

    @staticmethod
    def validar_nombre(nombre):
        if not re.match(nombre_regex, nombre):
            raise ValueError('El nombre debe contener al menos nombre y apellido')
        return nombre.lower()
    
    @staticmethod
    def validar_formato_correo(correo):
        if not re.match(correo_regex, correo):
            raise ValueError('Formato de correo electrónico inválido')
        return correo.lower()

    @staticmethod
    def validar_telefono(telefono):
        if not re.match(telefono_regex, telefono):
            raise ValueError('El teléfono debe contener solo números (10-15 dígitos)')
        return telefono

    @staticmethod
    def validar_estadoEnEmpresa(estadoEnEmpresa):
        estado = int(estadoEnEmpresa)
        estados_validos = list(estadoEnEmpresaDict.keys())
        if estado not in estados_validos:
            raise ValueError(f'Estado inválido. estados válidos: {estados_validos}')
        return estado
    
    @staticmethod
    def validar_estadoCuenta(estadoCuenta):
        estadoCuenta = int(estadoCuenta)
        estados_validos = list(estadoCuentaDict.keys())
        if estadoCuenta not in estados_validos:
            raise ValueError(f'Estado inválido. estados válidos: {estados_validos}')
        return estadoCuenta

    @staticmethod
    def validar_estadoTicket(estadoTicket):
        estadoTicket = int(estadoTicket)
        estados_validos = list(estadoTicketDict.keys())
        if estadoTicket not in estados_validos:
            raise ValueError(f'Estado inválido. estados válidos: {estados_validos}')
        return estadoTicket

    def validar_prioridadTicket(prioridadTicket):
        prioridadTicket = int(prioridadTicket)
        estados_validos = list(prioridadTicketDict.keys())
        if prioridadTicket not in estados_validos:
            raise ValueError(f'Estado inválido. estados válidos: {estados_validos}')
        return prioridadTicket
    
    def validar_fecha(fecha):
        """Convierte la fecha a datetime y valida el formato, aceptando fechas con o sin hora."""
        formatos = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]
        for formato in formatos:
            try:
                return datetime.strptime(fecha, formato)
            except ValueError:
                continue
        raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, DD/MM/YYYY ó DD/MM/YYYY HH:MM:SS")

    @staticmethod
    def validar_idEmpresaExistente(idEmpresa):
        """Convierte el ID a UUID y valida que la empresa exista."""
        from models.Mongo.MongoModel import MongoModel

        try:
            if not isinstance(idEmpresa, UUID):
                idEmpresa = UUID(idEmpresa)

            empresa = MongoModel.obtener_empresa_por_id(idEmpresa)
            if not empresa:
                raise ValueError(f"La empresa con ID {idEmpresa} no existe.")
            return empresa
        except ValueError as e:
            raise ValueError(f"El ID ingresado no es un UUID válido. Error:{e}")

    @staticmethod
    def validar_idAgenteExistente(idAgente):
        """Convierte el ID a UUID y valida que el agente exista."""
        from models.Mongo.MongoModel import MongoModel

        try:
            if not isinstance(idAgente, UUID):
                idAgente = UUID(idAgente)

            agente = MongoModel.obtener_agente_por_id(idAgente)
            if not agente:
                raise ValueError(f"El agente con ID {idAgente} no existe.")
            return agente
        except ValueError as e:
            raise ValueError(f"El ID ingresado no es un UUID válido. Error:{e}")

    @staticmethod
    def validar_idClienteExistente(idCliente):
        """Convierte el ID a UUID y valida que el cliente exista."""
        from models.Mongo.MongoModel import MongoModel

        try:
            if not isinstance(idCliente, UUID):
                idCliente = UUID(idCliente)

            cliente = MongoModel.obtener_cliente_por_id(idCliente)
            if not cliente:
                raise ValueError(f"El cliente con ID {idCliente} no existe.")
            return cliente
        except ValueError as e:
            raise ValueError(f"El ID ingresado no es un UUID válido. Error:{e}")

    @staticmethod
    def validar_idTicketExistente(idTicket):
        """Convierte el ID a UUID y valida que el ticket exista."""
        from models.Mongo.MongoModel import MongoModel

        try:
            if not isinstance(idTicket, UUID):
                idTicket = UUID(idTicket)

            cliente = MongoModel.obtener_ticket_por_id(idTicket)
            if not cliente:
                raise ValueError(f"El ticket con ID {idTicket} no existe.")
            return cliente
        except ValueError as e:
            raise ValueError(f"El ID ingresado no es un UUID válido. Error:{e}")

    @staticmethod
    def validar_camposActualizacion(cambios: dict, campos_permitidos: list):
        # Filtrar solo los campos permitidos para actualizar
        cambios_filtrados = {k: v for k, v in cambios.items() if k in campos_permitidos}

        if not cambios_filtrados:
            raise ValueError("No se proporcionaron campos válidos para actualizar.")
    
        return cambios_filtrados

    @staticmethod
    def validar_ubicacion(ubicacion):
        try:
            if re.match(ubicacion_regex, ubicacion):
                longitud_str, latitud_str = ubicacion.split(',')
                longitud = float(longitud_str.strip())
                latitud = float(latitud_str.strip())
                return [longitud, latitud]
            else:
                raise ValueError
        except ValueError:
            raise ValueError(
                f"Ubicación inválida: {ubicacion}. Debe seguir el formato 'longitud,latitud' con rangos válidos."
            )


    #Tipo de problema
    @staticmethod
    def validar_tipoProblema(tipo: str):
        try:
            tipo_int = int(tipo)
            if tipo_int not in tipoProblema:
                raise ValueError(f"Tipo debe estar entre {list(tipoProblema.keys())}")
            return tipo_int
        except ValueError:
            raise ValueError("Debe ingresar un número válido")