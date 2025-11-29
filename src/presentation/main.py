import sys
import os

# CONFIGURACIÓN DE RUTAS (IMPORTANTE: No borrar)
# Permite importar archivos de carpetas hermanas como 'utils' o 'business'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar los menús que acabamos de crear
from presentation.menu_options import (
    MAIN_MENU, MENU_REGISTROS, MENU_ACTUALIZACIONES, 
    MENU_AGENTES, MENU_CLIENTES, MENU_TICKETS, MENU_EMPRESAS, 
    mostrar_menu
)

# Intentar importar validaciones (si ya moviste la carpeta utils)
try:
    from utils.validaciones import Validaciones, solicitar_input
except ImportError:
    # Si aún no existe, usamos input simple para que no falle
    def solicitar_input(msg, func=None): return input(msg)

# -----------------------------------------------------------------------------
# FUNCIONES DE FLUJO (SUB-MENÚS)
# -----------------------------------------------------------------------------

def procesar_registros():
    while True:
        mostrar_menu(MENU_REGISTROS)
        try:
            op = int(input("Seleccione una opción:"))
            if op == 0: break
            
            # Aquí irán las llamadas a la lógica de negocio (Service)
            if op == 1: 
                print("Creando Agente... (Pendiente de conectar)")
            elif op == 2: 
                print("Creando Cliente... (Pendiente de conectar)")
            elif op == 3: 
                print("Creando Ticket... (Pendiente de conectar)")
            elif op == 4: 
                print("Creando Empresa... (Pendiente de conectar)")
            else: 
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Ingrese un número válido")

def procesar_consultas_agentes():
    while True:
        mostrar_menu(MENU_AGENTES)
        try:
            op = int(input("Seleccione una opción: "))
            if op == 0: break
            
            if op == 1:
                nombre = input("Ingrese nombre: ")
                print(f"Buscando a {nombre}... (Pendiente)")
            else:
                print("Opción seleccionada (Lógica pendiente)")
        except ValueError:
            print("❌ Ingrese un número válido")

def procesar_consultas_clientes():
    while True:
        mostrar_menu(MENU_CLIENTES)
        try:
            op = int(input("Seleccione una opción: "))
            if op == 0: 
                break
            print("Módulo Clientes en construcción")
        except ValueError:
            print("❌ Ingrese un número válido")

def procesar_consultas_tickets():
    while True:
        mostrar_menu(MENU_TICKETS)
        try:
            op = int(input("Seleccione una opción: "))
            if op == 0: break
            print(">> Módulo Tickets en construcción")
        except ValueError:
            print("❌ Ingrese un número válido")

def procesar_consultas_empresas():
    while True:
        mostrar_menu(MENU_EMPRESAS)
        try:
            op = int(input("Seleccione una opción: "))
            if op == 0: 
                break
            print(">> Módulo Empresas en construcción")
        except ValueError:
            print("❌ Ingrese un número válido")

def procesar_actualizaciones():
    while True:
        mostrar_menu(MENU_ACTUALIZACIONES)
        try:
            op = int(input(">> Seleccione una opción: "))
            if op == 0: break
            print(">> Módulo Actualizaciones en construcción")
        except ValueError:
            print("❌ Ingrese un número válido")

# -----------------------------------------------------------------------------
# BUCLE PRINCIPAL
# -----------------------------------------------------------------------------
def main():
    print("\n*************************************************")
    print("* CUSTOMER SUPPORT SYSTEM (REFACTORIZADO)     *")
    print("*************************************************")

    while True:
        mostrar_menu(MAIN_MENU)
        try:
            op_txt = input("Seleccione una opción principal: ")
            if not op_txt.isdigit():
                print("❌ Error: Ingrese un número.")
                continue
            
            op = int(op_txt)

            if op == 8:
                print("👋 Saliendo...")
                break
            elif op == 0: 
                print("ℹ️ Poblado de datos movido a script administrativo.")
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
                print("⚠️  Eliminación deshabilitada por seguridad.")
            else: 
                print("❌ Opción no reconocida.")

        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    main()