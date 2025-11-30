MAIN_MENU = {
    0: "Poblar de datos",
    1: "Registros",
    2: "Actualizaciones",
    3: "Consultas de agentes",
    4: "Consultas de clientes",
    5: "Consultas de tickets",
    6: "Consultas de empresas",
    7: "Eliminar bases de datos",
    8: "Salir"
}

MENU_REGISTROS = {
    0: "Regresar a menú principal",
    1: "Registro de Agente",
    2: "Registro de Cliente",
    3: "Registro de Ticket",
    4: "Registro de Empresa"
}

MENU_ACTUALIZACIONES = {
    0: "Regresar a menú principal",
    1: "Actualizar Agente",
    2: "Actualizar Cliente",
    3: "Actualizar Ticket"
}

MENU_AGENTES = {
    0: "Regresar a menú principal",
    1: "Obtener información de agente en base a su nombre",
    2: "Obtener información de agente en base a su ID",
    3: "Mostrar agentes por empresa",
    4: "Mostrar agente por ticket",
    5: "Historial de estado en empresa de agente"
}

MENU_CLIENTES = {
    0: "Regresar a menú principal",
    1: "Obtener información de cliente en base a su nombre",
    2: "Obtener información de cliente en base a su ID",
    3: "Mostrar información de clientes y IDs de tickets de una empresa...",
    4: "Mostrar clientes por empresa",
    5: "Mostrar cliente por ticket",
    6: "Historial de estado de cuenta de cliente"
}

MENU_TICKETS = {
    0:  "Regresar a menú principal",
    1:  "Obtener información de ticket en base a su ID",
    2:  "Mostrar Tickets con estado “Cerrado” por Agente",
    3:  "Mostrar Tickets con estado “En proceso” por Agente",
    4:  "Mostrar Tickets con estado “Cerrado” por Empresa",
    5:  "Mostrar Tickets con estado “En proceso” por Empresa",
    6:  "Mostrar Tickets con estado “Abierto” por Empresa",
    7:  "Mostrar Tickets con estado “Cerrado” por Cliente.",
    8:  "Mostrar Tickets con estado “En proceso” por Cliente.",
    9:  "Mostrar Tickets con estado “Abierto” por Cliente.",
    10: "Filtrar tickets de empresa por prioridad",
    11: "Mostrar tickets de una empresa con una antigüedad mayor a “x” fecha",
    12: "Mostrar tickets cerrados en un periodo de tiempo por agente",
    13: "Obtener la cantidad de tickets...",
    14: "Obtener la cantidad de tickets que ha cerrado un agente...",
    15: "Mostrar tickets por empresa",
    16: "Mostrar tickets por cliente",
    17: "Mostrar tickets de una empresa por tipo de problema ",
    18: "Mostrar tickets de un agente de una empresa por tipo de problema ",
    19: "Búsqueda de Ticket por empresa por medio de palabras clave",
    20: "Búsqueda de Ticket por Agente y Empresa por medio de palabras clave",
    21: "Historial de comentarios de ticket en base al id del ticket",
    22: "Historial de cambios en la prioridad de un ticket",
    23: "Historial de asignación de agentes a un ticket",
    24: "Historial de estados del ticket",
    25: "Historial de tickets creados en empresa",
    26: "Historial de tickets creados en empresa después de x fecha"
}

MENU_EMPRESAS = {
    0: "Regresar a menú principal",
    1: "Obtener información de empresa en base a su nombre",
    2: "Obtener información de empresa en base a su id",
    3: "Mostrar ubicación de la empresa por medio de su id"
}


def mostrar_menu(opciones_dict):
    """Función auxiliar para imprimir cualquier menú de forma limpia"""
    print("\n" + "="*40)
    for key, value in opciones_dict.items():
        print(f"{key} -- {value}")
    print("="*40 + "\n")
