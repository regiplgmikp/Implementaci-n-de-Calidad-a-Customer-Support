import re
from datetime import datetime


class Validaciones:
    """
    Clase utilitaria para validar entradas de usuario.
    Cumple con el criterio de Usabilidad y Robustez del Plan de Calidad.
    """

    @staticmethod
    def validar_entero(valor):
        """Verifica que el valor sea un número entero positivo."""
        try:
            numero = int(valor)
            if numero < 0:
                print("❌ Error: El número no puede ser negativo.")
                return False
            return True
        except ValueError:
            print("❌ Error: Debe ingresar un número entero válido.")
            return False

    @staticmethod
    def validar_no_vacio(valor):
        """Verifica que el texto no esté vacío o sea solo espacios."""
        if not valor or not valor.strip():
            print("❌ Error: Este campo no puede estar vacío.")
            return False
        return True

    @staticmethod
    def validar_email(email):
        """Valida el formato de correo electrónico usando Expresiones Regulares."""
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(patron, email):
            return True
        print("❌ Error: Formato de correo inválido (ejemplo: usuario@dominio.com).")
        return False

    @staticmethod
    def validar_fecha(fecha_str):
        """Valida que la fecha tenga formato YYYY-MM-DD."""
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return True
        except ValueError:
            print("❌ Error: Formato de fecha inválido. Use YYYY-MM-DD.")
            return False

    @staticmethod
    def validar_opcion_menu(opcion, max_opcion):
        """Verifica que la opción esté dentro del rango del menú."""
        if Validaciones.validar_entero(opcion):
            val = int(opcion)
            if 0 <= val <= max_opcion:
                return True
            print(f"❌ Error: La opción debe estar entre 0 y {max_opcion}.")
        return False


def solicitar_input(mensaje, funcion_validacion=None):
    """
    Función helper que mantiene al usuario en un bucle hasta que
    ingrese un dato válido según la función de validación proporcionada.
    """
    while True:
        valor = input(mensaje)
        # Si no hay validación específica, solo checamos que no esté vacío
        if funcion_validacion is None:
            if Validaciones.validar_no_vacio(valor):
                return valor
        else:
            # Si hay función de validación, la ejecutamos
            if funcion_validacion(valor):
                return valor
