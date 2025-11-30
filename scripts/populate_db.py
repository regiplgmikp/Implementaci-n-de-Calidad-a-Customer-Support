import os
import sys
import time

# Configuración de rutas (Para que el orquestador encuentre los scripts hermanos)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importamos las funciones de poblado y eliminación de cada script especializado
# Nota: La importación se hace al inicio para verificar que los archivos existan.
try:
    from scripts.poblar_mongo import poblar_mongo, eliminar_mongo
    from scripts.poblar_cassandra import poblar_cassandra, eliminar_cassandra
    from scripts.poblar_dgraph import poblar_dgraph, drop_all

    # Importamos el Repositorio de Mongo para las operaciones de limpieza (Drop Database)
    from data_access.repositories.mongo_repo import MongoRepository

except ImportError as e:
    print(f"❌ ERROR CRÍTICO DE IMPORTACIÓN: {e}")
    print("Asegúrese de que los archivos para poblar estén en la carpeta 'scripts/'.")
    exit(1)  # Salimos si no se pueden importar los módulos críticos


def eliminar_bases():
    """Ejecuta la eliminación de datos en las 3 bases de datos."""
    print("\n\n--------------------------------------------------")
    print("💥 INICIANDO ELIMINACIÓN DE DATOS...")

    # Mongo: Elimina la base de datos completa
    try:
        eliminar_mongo()
        print("   ✅ Mongo: Base de datos eliminada.")
    except Exception as e:
        print(f"   ❌ Mongo: Falló la eliminación: {e}")

    # Cassandra: Elimina el Keyspace completo
    try:
        eliminar_cassandra()
        print("   ✅ Cassandra: Keyspace eliminado.")
    except Exception as e:
        print(f"   ❌ Cassandra: Falló la eliminación: {e}")

    # Dgraph: Elimina el esquema y todos los datos
    try:
        # Creamos una instancia para acceder al cliente Dgraph
        dgraph_client = MongoRepository().client
        drop_all(dgraph_client)
    except Exception as e:
        print(f"   ❌ Dgraph: Falló la eliminación: {e}")

    print("✅ Proceso de eliminación finalizado.")


def poblar_todo():
    """Ejecuta el poblado de datos en las 3 bases de datos en orden."""
    print("\n\n==================================================")
    print("🚀 INICIANDO POBLADO DE DATOS MAESTRO (Mongo, Cass, Dgraph)")
    print("==================================================")

    # ------------------------------------------------------------------
    # 1. LIMPIEZA INICIAL
    # ------------------------------------------------------------------

    confirmacion = input(
        "¿Desea ELIMINAR los datos existentes antes de poblar? (y/n): "
    )
    if confirmacion.lower() == "y":
        eliminar_bases()
        time.sleep(3)  # Pausa para que las BBDD se recuperen del DROP

    # ------------------------------------------------------------------
    # 2. POBLADO SECUENCIAL
    # Orden: Mongo (fuente de verdad) -> Dgraph (relaciones) -> Cassandra (historial)
    # ------------------------------------------------------------------

    print("\n[FASE 1: MONGODB - Entidades Maestras]")
    poblar_mongo()
    time.sleep(1)

    print("\n[FASE 2: DGRAPH - Nodos y Relaciones]")
    poblar_dgraph()
    time.sleep(1)

    print("\n[FASE 3: CASSANDRA - Historiales y Time-Series]")
    poblar_cassandra()

    print("\n==================================================")
    print("🎉 POBLADO DE DATOS MAESTRO FINALIZADO CON ÉXITO.")
    print("==================================================")


if __name__ == "__main__":
    # Esta es la función que debe ser llamada al ejecutar el script
    poblar_todo()
