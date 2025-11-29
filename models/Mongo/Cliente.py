from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4
from models.Utils.validaciones import Validaciones

class ClienteValidationError(Exception):
    """Excepción personalizada para errores de validación de Clientes"""
    def __init__(cls, message="Error de validación en datos del Cliente"):
        cls.message = message
        super().__init__(cls.message)

class Cliente(BaseModel):
    idCliente: UUID = Field(default_factory=uuid4) # Si no se proporciona un ID, se genera uno nuevo
    nombre: str
    correo: str
    telefono: str
    estadoCuenta: int
    idEmpresa: UUID

    def __str__(self):
        result = f"""
    IdCliente: {self.idCliente}
    Nombre: {self.nombre}
    Correo: {self.correo}
    Teléfono: {self.telefono}
    Estado de cuenta: {self.estadoCuenta}
    IdEmpresa: {self.idEmpresa}"""
        return result

    @field_validator('nombre')
    def validar_nombre_completo(nombre):
        return Validaciones.validar_nombre(nombre)
    
    @field_validator('correo')
    def validar_formato_correo(correo):
        return Validaciones.validar_formato_correo(correo)

    @field_validator('telefono')
    def validar_telefono(telefono):
        return Validaciones.validar_telefono(telefono)

    @field_validator('estadoCuenta')
    def validar_estadoCuenta(estadoCuenta):
        return Validaciones.validar_estadoCuenta(estadoCuenta)

    @field_validator('idEmpresa')
    def validar_idEmpresa(idEmpresa):
        return Validaciones.validar_idEmpresaExistente(idEmpresa).idEmpresa

    @classmethod
    def crear_desde_dict(cls, data: dict):
        try:
            return cls(**data)
        except Exception as e:
            raise ClienteValidationError(str(e))