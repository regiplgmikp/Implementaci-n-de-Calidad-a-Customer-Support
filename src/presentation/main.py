import sys
import os

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# -----------------------------------------------------------------------------
# Obtenemos la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ruta a 'src'
src_path = os.path.abspath(os.path.join(current_dir, ".."))
# Ruta a la RAÍZ del proyecto
root_path = os.path.abspath(os.path.join(src_path, ".."))

# Agregamos ambas rutas al sistema para poder importar todo
sys.path.append(src_path)
sys.path.append(root_path)

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------

from presentation.menu_options import (  # noqa: E402
    MAIN_MENU,
    MENU_REGISTROS,
    MENU_AGENTES,
    mostrar_menu,
)

# Importamos el Servicio (El Cerebro)
from business.support_service import SupportService  # noqa: E402

# Importamos el Orquestador de Poblado (Opción 0)
try:
    from scripts.populate_db import poblar_todo  # noqa: E402
except ImportError:
    # Fallback para no romper el programa si el script no está listo
    def poblar_todo():
        print("⚠️ El script 'scripts/populate_db.py' no se encuentra.")


# Intentamos importar validaciones
try:
    from utils.validaciones import Validaciones, solicitar_input  # noqa: E402
except ImportError:
    # Fallback por si acaso falla el import
    def solicitar_input(msg, _=None):
        return input(msg)

    class Validaciones:
        @staticmethod
        def validar_no_vacio(x):
            return True

        @staticmethod
        def validar_email(x):
            return True

        @staticmethod
        def validar_entero(x):
            return x.isdigit()


# Instancia global del servicio para usar en todo el menú
service = None


def inicializar_servicio():
    global service
    if service is None:
        try:
            service = SupportService()
        except Exception as e:
            print(f"❌ Error conectando a bases de datos: {e}")
            print("⚠️ El sistema funcionará limitado.")


# -----------------------------------------------------------------------------
# FUNCIONES DE FLUJO
# -----------------------------------------------------------------------------


def procesar_registros():
    while True:
        mostrar_menu(MENU_REGISTROS)
        try:
            op_str = solicitar_input(
                ">> Seleccione una opción: ", Validaciones.validar_entero
            )
            op = int(op_str)

            if op == 0:
                break

            if service is None:
                print("❌ Error: No hay conexión a los servicios.")
                continue

            # 1. REGISTRO DE AGENTE
            if op == 1:
                print("\n--- Nuevo Agente ---")
                nombre = solicitar_input("Nombre: ", Validaciones.validar_no_vacio)
                email = solicitar_input("Email: ", Validaciones.validar_email)
                rol = solicitar_input(
                    "Rol (Soporte/Admin): ", Validaciones.validar_no_vacio
                )

                uid = service.registrar_agente(nombre, email, rol)
                if uid:
                    print(f"✨ ¡Agente registrado! ID Interno: {uid}")

            # 2. REGISTRO DE CLIENTE
            elif op == 2:
                print("\n--- Nuevo Cliente ---")
                nombre = solicitar_input("Nombre: ", Validaciones.validar_no_vacio)
                email = solicitar_input("Email: ", Validaciones.validar_email)
                tel = solicitar_input("Teléfono: ", Validaciones.validar_no_vacio)

                uid = service.registrar_cliente(nombre, email, tel)
                if uid:
                    print(f"✨ ¡Cliente registrado! ID: {uid}")

            # 3. REGISTRO DE TICKET
            elif op == 3:
                print("\n--- Nuevo Ticket ---")
                id_cliente = solicitar_input(
                    "ID Cliente: ", Validaciones.validar_no_vacio
                )
                titulo = solicitar_input("Título: ", Validaciones.validar_no_vacio)
                desc = solicitar_input("Descripción: ", Validaciones.validar_no_vacio)
                prio = solicitar_input("Prioridad: ", Validaciones.validar_no_vacio)

                uid = service.registrar_ticket(titulo, desc, prio, id_cliente)
                if uid:
                    print(f"🎫 Ticket creado exitosamente. ID: {uid}")

            elif op == 4:
                print(">> (Opción Empresa pendiente)")
            else:
                print("❌ Opción inválida")

        except ValueError:
            print("❌ Ingrese un número válido")


def procesar_consultas_agentes():
    while True:
        mostrar_menu(MENU_AGENTES)
        try:
            op_str = solicitar_input(
                ">> Seleccione una opción: ", Validaciones.validar_entero
            )
            op = int(op_str)

            if op == 0:
                break

            if op == 1:
                nombre = solicitar_input(
                    "Ingrese nombre: ", Validaciones.validar_no_vacio
                )
                agente = service.obtener_agente(nombre, por_id=False)
                if agente:
                    print(f"\n✅ Agente Encontrado:\n{agente}")
                else:
                    print("❌ No se encontró el agente.")

            elif op == 2:
                uid = solicitar_input("Ingrese ID: ", Validaciones.validar_no_vacio)
                agente = service.obtener_agente(uid, por_id=True)
                if agente:
                    print(f"\n✅ Agente Encontrado:\n{agente}")
                else:
                    print("❌ ID no encontrado.")
            else:
                print(">> Opción en construcción")
        except ValueError:
            print("❌ Error de entrada")


# Definimos las funciones stubs
def procesar_consultas_clientes():
    print("Módulo en construcción de clientes")
    input("Enter...")


def procesar_consultas_tickets():
    print("Módulo en construcción de tickets")
    input("Enter...")


def procesar_consultas_empresas():
    print("Módulo en construcción de empresas")
    input("Enter...")


def procesar_actualizaciones():
    print("Módulo en construcción de actualizaciones")
    input("Enter...")


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    print("\n*************************************************")
    print("* CUSTOMER SUPPORT SYSTEM (REFACTORIZADO)     *")
    print("*************************************************")

    inicializar_servicio()

    while True:
        mostrar_menu(MAIN_MENU)
        try:
            op_txt = input("Seleccione una opción principal: ")
            if not op_txt.isdigit():
                print("❌ Debe ingresar un número.")
                continue
            op = int(op_txt)

            if op == 8:
                print("👋 Saliendo...")
                if service:
                    service.cerrar_conexiones()
                break
            elif op == 0:
                # AQUÍ ESTÁ LA MAGIA: Llamamos al orquestador
                poblar_todo()
                # Re-inicializamos el servicio por si se cerraron conexiones
                inicializar_servicio()
            elif op == 1:
                procesar_registros()
            elif op == 2:
                procesar_actualizaciones()
            elif op == 3:
                procesar_consultas_agentes()
            elif op == 4:
                procesar_consultas_clientes()
            elif op == 5:
                procesar_consultas_tickets()
            elif op == 6:
                procesar_consultas_empresas()
            elif op == 7:
                print("⚠️ Opción deshabilitada.")
            else:
                print("❌ Opción no reconocida.")

        except Exception as e:
            print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
