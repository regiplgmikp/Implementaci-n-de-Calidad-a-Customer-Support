from pydantic import BaseModel, Field, field_validator, model_validator
from uuid import UUID, uuid4
from datetime import datetime
from models.Utils.validaciones import Validaciones

class TicketValidationError(Exception):
    """Excepción personalizada para errores de validación de Tickets"""
    def __init__(cls, message="Error de validación en datos del Ticket"):
        cls.message = message
        super().__init__(cls.message)

class Ticket(BaseModel):
    idTicket: UUID = Field(default_factory=uuid4)
    idCliente: UUID
    idAgente: UUID | None = None
    idEmpresa: UUID
    fechaCreacion: datetime
    fechaCierre: datetime | None = None
    comentarios: list[str] | None = []
    estado: int
    prioridad: int

    def __str__(self):
        result =  f"""
    idTicket: {self.idTicket}
    idCliente: {self.idCliente}
    idAgente: {self.idAgente}
    idEmpresa: {self.idEmpresa}
    fechaCreacion: {self.fechaCreacion}
    fechaCierre: {self.fechaCierre}
    comentarios: {self.comentarios}
    estado: {self.estado}
    prioridad: {self.prioridad}"""
        return result

    # Validar que entidades relacionadas a UUIDs existan
    @field_validator('idCliente')
    def validar_idCliente(idCliente):
        return Validaciones.validar_idClienteExistente(idCliente).idCliente

    @field_validator('idAgente')
    def validar_idAgente(idAgente):
        if idAgente:
            return Validaciones.validar_idAgenteExistente(idAgente).idAgente
        return None

    @field_validator('idEmpresa')
    def validar_idEmpresa(idEmpresa):
        return Validaciones.validar_idEmpresaExistente(idEmpresa).idEmpresa

    @model_validator(mode='after')
    def validar_fechas(self):
        if self.fechaCierre and self.fechaCierre < self.fechaCreacion:
            raise ValueError("La fecha de cierre no puede ser anterior a la fecha de creación")
        return self

    @field_validator('estado')
    def validar_estado(estado):
        return Validaciones.validar_estadoTicket(estado)

    @field_validator('prioridad')
    def validar_prioridad(prioridad):
        return Validaciones.validar_prioridadTicket(prioridad)

    @classmethod
    def crear_desde_dict(cls, data: dict):
        try:
            return cls(**data)
        except Exception as e:
            raise TicketValidationError(str(e))