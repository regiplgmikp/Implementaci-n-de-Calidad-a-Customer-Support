import sys
import os

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# -----------------------------------------------------------------------------
# Obtenemos la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ruta a 'src'
src_path = os.path.abspath(os.path.join(current_dir, ".."))
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
    MENU_TICKETS,
    mostrar_menu,
)

# Importamos el Servicio (El Cerebro)
from business.support_service import SupportService  # noqa: E402# noqa: E402

# Importamos el Orquestador de Poblado (Opción 0)
try:
    from scripts.populate_db import poblar_todo  # noqa: E402
except ImportError:
    # Fallback para no romper el programa si el script no está listo
    def poblar_todo():
        print("⚠️ El script 'scripts/populate_db.py' no se encuentra.")


# Importamos validaciones con fallback
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
        def validar_entero(x):
            return x.isdigit()

        @staticmethod
        def validar_email(x):
            return True


# Instancia global del servicio
service = None


def inicializar_servicio():
    global service
    if service is None:
        try:
            service = SupportService()
        except Exception as e:
            print(f"❌ Error conectando a bases de datos: {e}")


# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE REGISTRO (Helpers para reducir complejidad)
# -----------------------------------------------------------------------------


def _registrar_agente():
    # 1. REGISTRO DE AGENTE
    print("\n--- Nuevo Agente ---")
    nombre = solicitar_input("Nombre: ", Validaciones.validar_no_vacio)
    email = solicitar_input("Email: ", Validaciones.validar_email)
    rol = solicitar_input("Rol (Soporte/Admin): ", Validaciones.validar_no_vacio)

    # Se registra en Mongo, Cassandra y Dgraph
    uid = service.registrar_agente(nombre, email, rol)
    if uid:
        print(f"✨ ¡Agente registrado! ID Interno: {uid}")


def _registrar_cliente():
    # 2. REGISTRO DE CLIENTE
    print("\n--- Nuevo Cliente ---")
    nombre = solicitar_input("Nombre: ", Validaciones.validar_no_vacio)
    email = solicitar_input("Email: ", Validaciones.validar_email)
    tel = solicitar_input("Teléfono: ", Validaciones.validar_no_vacio)

    # Se registra en Mongo, Cassandra y Dgraph
    uid = service.registrar_cliente(nombre, email, tel)
    if uid:
        print(f"✨ ¡Cliente registrado! ID: {uid}")


def _registrar_ticket():
    # 3. REGISTRO DE TICKET
    print("\n--- Nuevo Ticket ---")
    id_cliente = solicitar_input("ID Cliente: ", Validaciones.validar_no_vacio)
    titulo = solicitar_input("Título: ", Validaciones.validar_no_vacio)
    desc = solicitar_input("Descripción: ", Validaciones.validar_no_vacio)
    prio = solicitar_input("Prioridad (1-4): ", Validaciones.validar_entero)

    # Se registra en Mongo, Cassandra y Dgraph
    uid = service.registrar_ticket(titulo, desc, int(prio), id_cliente)
    if uid:
        print(f"🎫 Ticket creado exitosamente. ID: {uid}")


def procesar_registros():
    """Controlador de Registros Refactorizado"""
    while True:
        mostrar_menu(MENU_REGISTROS)
        try:
            op_str = solicitar_input(">> Opción: ", Validaciones.validar_entero)
            op = int(op_str)

            if op == 0:
                break
            if not service:
                print("❌ Sin conexión.")
                break

            if op == 1:
                _registrar_agente()
            elif op == 2:
                _registrar_cliente()
            elif op == 3:
                _registrar_ticket()
            elif op == 4:
                print(">> (Opción Empresa pendiente)")
            else:
                print("❌ Opción inválida")

        except ValueError:
            print("❌ Error de entrada")


# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE CONSULTAS AGENTES
# -----------------------------------------------------------------------------


def _buscar_agente_por_nombre():
    # "Obtener información de agente en base a su nombre" # Mongo
    nombre = solicitar_input("Ingrese nombre: ", Validaciones.validar_no_vacio)
    agente = service.obtener_agente(nombre, por_id=False)
    if agente:
        print(f"\n✅ Agente:\n{agente}")
    else:
        print("❌ No encontrado.")


def _buscar_agente_por_id():
    # "Obtener información de agente en base a su ID" # Mongo
    uid = solicitar_input("ID: ", Validaciones.validar_no_vacio)
    agente = service.obtener_agente(uid, por_id=True)
    if agente:
        print(f"\n✅ Agente:\n{agente}")
    else:
        print("❌ No encontrado.")


def procesar_consultas_agentes():
    # Consultas de agentes
    while True:
        mostrar_menu(MENU_AGENTES)
        try:
            op = int(solicitar_input(">> Opción: ", Validaciones.validar_entero))
            if op == 0:
                break
            elif op == 1:
                _buscar_agente_por_nombre()
            elif op == 2:
                _buscar_agente_por_id()
            elif op == 3:
                print(">> Mostrar agentes por empresa (Dgraph) - Pendiente")
            elif op == 4:
                print(">> Mostrar agente por ticket (Dgraph) - Pendiente")
            elif op == 5:
                print(">> Historial de estado en empresa (Cassandra) - Pendiente")
            else:
                print(">> Opción en construcción")
        except ValueError:
            print("❌ Error")


# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE TICKETS (Persistencia Políglota)
# -----------------------------------------------------------------------------


def _ver_historial_ticket():
    # Opciones 21-24: Historiales # Cassandra
    tid = solicitar_input("ID Ticket: ", Validaciones.validar_no_vacio)
    hist = service.ver_traza_ticket(tid)
    if hist:
        print(f"\n📜 HISTORIAL CASSANDRA ({len(hist)} eventos):")
        for h in hist:
            print(
                f"   {h.fecha} | {h.estado_anterior} -> {h.estado_nuevo} | User: {h.usuario_id}"
            )
    else:
        print("📜 Sin historial.")


def _buscar_ticket_keyword():
    # "Búsqueda de Ticket por empresa por medio de palabras clave" # Dgraph
    kw = solicitar_input("Palabra clave: ", Validaciones.validar_no_vacio)
    res = service.buscar_tickets_avanzado(kw)
    if res:
        print(f"\n DGRAPH RESULTADOS ({len(res)}):")
        for r in res:
            print(f"   [{r.get('idTicket')}] {r.get('descripcion')[:40]}...")
    else:
        print("🕸️  Sin coincidencias.")


def _buscar_ticket_mongo_id():
    # "Obtener información de ticket en base a su ID" # Mongo
    tid = solicitar_input("ID Ticket: ", Validaciones.validar_no_vacio)
    t = service.obtener_ticket_por_id(tid)
    print(f"🎫 TICKET: {t}" if t else "❌ No existe.")


def procesar_consultas_tickets():
    # Consultas de tickets
    while True:
        mostrar_menu(MENU_TICKETS)
        try:
            op = int(solicitar_input(">> Opción: ", Validaciones.validar_entero))
            if op == 0:
                break

            if op == 1:
                _buscar_ticket_mongo_id()

            # Consultas MongoDB (Filtros simples)
            elif op in [2, 3, 4, 5, 6, 7, 8, 9]:
                print(">> Filtros por estado/entidad (Mongo) - Implementado en Service")
                # Aquí iría la llamada a service.filtrar_tickets()

            # Consultas Dgraph (Grafos y Keywords)
            elif op == 19:
                _buscar_ticket_keyword()
            elif op in [15, 16, 17, 18, 20]:
                print(">> Consultas avanzadas de relaciones (Dgraph) - Pendiente")

            # Consultas Cassandra (Historiales)
            elif op in [21, 22, 23, 24]:
                _ver_historial_ticket()
            elif op in [25, 26]:
                print(">> Historial tickets por empresa (Cassandra) - Pendiente")

            else:
                print("⚠️ Opción no reconocida.")

        except ValueError:
            print("❌ Error")


# -----------------------------------------------------------------------------
# STUBS (Módulos pendientes de refactorizar)
# -----------------------------------------------------------------------------
def procesar_consultas_clientes():
    # Consultas de clientes
    print("🚧 Módulo de Clientes en construcción")
    input("Enter para continuar...")


def procesar_consultas_empresas():
    # Consultas de empresas
    print("🚧 Módulo de Empresas en construcción")
    input("Enter para continuar...")


def procesar_actualizaciones():
    # Actualizaciones
    print("🚧 Módulo de Actualizaciones en construcción")
    input("Enter para continuar...")


# -----------------------------------------------------------------------------
# MAIN (El Orquestador Principal)
# -----------------------------------------------------------------------------
def main():

    print("\n=================================================")
    print("   CUSTOMER SUPPORT SYSTEM (SQA REFACTORED)    ")
    print("=================================================")

    inicializar_servicio()

    while True:
        mostrar_menu(MAIN_MENU)
        try:
            op_txt = input(">> Seleccione opción: ")
            if not op_txt.isdigit():
                print("❌ Ingrese un número.")
                continue
            op = int(op_txt)

            # Salir
            if op == 8:
                print("👋 Cerrando sistema...")
                if service:
                    service.cerrar_conexiones()
                break

            # Poblar de datos (Orquestador de Scripts)
            elif op == 0:
                poblar_todo()
                inicializar_servicio()

            # Registros
            elif op == 1:
                procesar_registros()

            # Actualizaciones
            elif op == 2:
                procesar_actualizaciones()

            # Consultas de agentes
            elif op == 3:
                procesar_consultas_agentes()

            # Consultas de clientes
            elif op == 4:
                procesar_consultas_clientes()

            # Consultas de tickets
            elif op == 5:
                procesar_consultas_tickets()

            # Consultas de empresas
            elif op == 6:
                procesar_consultas_empresas()

            # Eliminar bases de datos
            elif op == 7:
                print("⚠️ Limpieza deshabilitada por seguridad.")

            else:
                print("❌ Opción no válida.")

        except Exception as e:
            print(f"❌ Error crítico en Main: {e}")


if __name__ == "__main__":
    main()
