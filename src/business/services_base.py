import logging
import sys


class BaseService:
    """
    Clase base para todos los servicios de negocio.
    Centraliza la configuración de logging y manejo básico de errores.
    """

    def __init__(self):
        # Configuración básica de Logging para ver qué pasa en consola
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_error(self, metodo, error):
        """Helper para estandarizar mensajes de error."""
        self.logger.error(f"Error en {metodo}: {str(error)}")

    def log_info(self, mensaje):
        """Helper para mensajes informativos."""
        self.logger.info(mensaje)
