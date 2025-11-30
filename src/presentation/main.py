import sys
import os

# Configuración de rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from presentation.menu_options import (
    MAIN_MENU, MENU_REGISTROS, MENU_ACTUALIZACIONES, 
    MENU_AGENTES, MENU_CLIENTES, MENU_TICKETS, MENU_EMPRESAS, 
    mostrar_menu
)

# Importamos el Servicio (El Cerebro)
from business.support_service import SupportService

# Intentamos importar validaciones
try:
    from utils.validaciones import Validaciones, solicitar_input
except ImportError:
    def solicitar_input(msg, func=None): return input(msg)

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
            op = int(input(">> Seleccione una opción: "))
            if op == 0: break
            
            if service is None:
                print("❌ Error: No hay conexión a los servicios.")
                continue

            # ---------------------------------------------------------
            # 1. REGISTRO DE AGENTE
            # ---------------------------------------------------------
            if op == 1: 
                print("\n--- Nuevo Agente ---")
                nombre = input("Nombre: ")
                email = input("Email: ")
                rol = input("Rol (Soporte/Admin): ")
                
                # ¡Llamada real al sistema!
                uid = service.registrar_agente(nombre, email, rol)
                if uid:
                    print(f"✨ ¡Agente registrado! ID Interno: {uid}")
            
            # ---------------------------------------------------------
            # 2. REGISTRO DE CLIENTE
            # ---------------------------------------------------------
            elif op == 2: 
                print("\n--- Nuevo Cliente ---")
                nombre = input("Nombre: ")
                email = input("Email: ")
                tel = input("Teléfono: ")
                
                uid = service.registrar_cliente(nombre, email, tel)
                if uid:
                    print(f"✨ ¡Cliente registrado! ID: {uid}")

            # ---------------------------------------------------------
            # 3. REGISTRO DE TICKET
            # ---------------------------------------------------------
            elif op == 3: 
                print("\n--- Nuevo Ticket ---")
                id_cliente = input("ID del Cliente que reporta: ")
                titulo = input("Título del problema: ")
                desc = input("Descripción detallada: ")
                prio = input("Prioridad (Alta/Media/Baja): ")
                
                uid = service.registrar_ticket(titulo, desc, prio, id_cliente)
                if uid:
                    print(f"🎫 Ticket creado exitosamente. ID: {uid}")

            elif op == 4: 
                print(">> (Opción Empresa pendiente de implementación en Service)")
            else: 
                print("❌ Opción inválida")

        except ValueError:
            print("❌ Ingrese un número válido")

def procesar_consultas_agentes():
    while True:
        mostrar_menu(MENU_AGENTES)
        try:
            op = int(input(">> Seleccione una opción: "))
            if op == 0: break
            
            if op == 1:
                nombre = input("Ingrese nombre: ")
                agente = service.obtener_agente(nombre, por_id=False)
                if agente:
                    print(f"\n✅ Agente Encontrado:\n{agente}")
                else:
                    print("❌ No se encontró el agente.")
            
            elif op == 2:
                uid = input("Ingrese ID: ")
                agente = service.obtener_agente(uid, por_id=True)
                if agente:
                    print(f"\n✅ Agente Encontrado:\n{agente}")
                else:
                    print("❌ ID no encontrado.")
            else:
                print(">> Opción en construcción")
        except ValueError:
            print("❌ Error de entrada")

def procesar_consultas_clientes(): print(">> Módulo en construcción"); input("Enter...")
def procesar_consultas_tickets(): print(">> Módulo en construcción"); input("Enter...")
def procesar_consultas_empresas(): print(">> Módulo en construcción"); input("Enter...")
def procesar_actualizaciones(): print(">> Módulo en construcción"); input("Enter...")

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    print("\n*************************************************")
    print("* CUSTOMER SUPPORT SYSTEM (REFACTORIZADO)     *")
    print("*************************************************")
    
    # Inicializamos conexiones
    inicializar_servicio()

    while True:
        mostrar_menu(MAIN_MENU)
        try:
            op_txt = input("Seleccione una opción principal: ")
            if not op_txt.isdigit():
                continue
            op = int(op_txt)

            if op == 8:
                print("👋 Saliendo...")
                if service: service.cerrar_conexiones()
                break
            elif op == 0: print("ℹ️  Use scripts/populate.py para carga masiva.")
            elif op == 1: procesar_registros()
            elif op == 2: procesar_actualizaciones()
            elif op == 3: procesar_consultas_agentes()
            elif op == 4: procesar_consultas_clientes()
            elif op == 5: procesar_consultas_tickets()
            elif op == 6: procesar_consultas_empresas()
            elif op == 7: print("⚠️ Opción deshabilitada.")
            else: print("❌ Opción no reconocida.")

        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    main()