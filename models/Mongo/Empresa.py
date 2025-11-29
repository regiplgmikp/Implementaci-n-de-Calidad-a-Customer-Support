from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4
from models.Utils.validaciones import Validaciones

class EmpresaValidationError(Exception):
    """Excepción personalizada para errores de validación de Empresas"""
    def __init__(cls, message="Error de validación en datos del Empresa"):
        cls.message = message
        super().__init__(cls.message)

class Empresa(BaseModel):
    idEmpresa: UUID = Field(default_factory=uuid4) # Si no se proporciona un ID, se genera uno nuevo
    nombre: str
    correo: str
    telefono: str
    direccion: str

    def __str__(self):
        result = f"""
    IdEmpresa: {self.idEmpresa}
    Nombre: {self.nombre}
    Correo: {self.correo}
    Teléfono: {self.telefono}
    Dirección: {self.direccion}"""
        return result
    
    @field_validator('correo')
    def validar_formato_correo(correo):
        return Validaciones.validar_formato_correo(correo)

    @field_validator('telefono')
    def validar_telefono(telefono):
        return Validaciones.validar_telefono(telefono)

    @classmethod
    def crear_desde_dict(cls, data: dict):
        try:
            return cls(**data)
        except Exception as e:
            raise EmpresaValidationError(str(e))