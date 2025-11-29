import csv
from uuid import UUID
from datetime import datetime
import ast
from models.Mongo.MongoModel import MongoModel

def populate_agentes(csv_path: str):
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        exitosos = 0
        errores = []    

        for num_fila, row in enumerate(csv_reader, 2):
            try:
                data = {
                    'idAgente': UUID(row['idAgente']),
                    'nombre': row['nombre'],
                    'correo': row['correo'],
                    'telefono': row['telefono'],
                    'estadoEnEmpresa': int(row['estadoEnEmpresa']),
                    'idEmpresa': UUID(row['idEmpresa']),
                    'fechaIngreso': datetime.strptime(
                        row['fechaIngreso'], 
                        '%Y-%m-%dT%H:%M:%S'
                    )
                }
                
                MongoModel.insertar_agente(data)

                exitosos += 1
                
            except Exception as e:
                errores.append({
                    'fila': num_fila,
                    'error': str(e),
                    'datos': row
                })

        result = []
        result.append(f"""
\nResultado de la importación de Agentes:
• Registros exitosos: {exitosos}
• Errores: {len(errores)}

""")
        
        if errores:
            result[0] += "Detalle de errores:"
            for error in errores[:3]:
                result[0] += f"""
Fila: {error['fila']}\nError: {error['error']}
Datos: {error['datos']}\n
"""
        result.append({
            'exitosos': exitosos,
            'errores': len(errores)
            })

    return result

def populate_empresas(csv_path: str):
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        exitosos = 0
        errores = []

        for num_fila, row in enumerate(csv_reader, 2):
            try:
                data = {
                    'idEmpresa': UUID(row['idEmpresa']),
                    'nombre': row['nombre'],
                    'correo': row['correo'],
                    'telefono': row['telefono'],
                    'direccion': row['direccion'],
                }
                
                MongoModel.insertar_empresa(data)

                exitosos += 1
                
            except Exception as e:
                errores.append({
                    'fila': num_fila,
                    'error': str(e),
                    'datos': row
                })


        result = []
        result.append(f"""
\nResultado de la importación de Empresas:
• Registros exitosos: {exitosos}
• Errores: {len(errores)}

""")
        
        if errores:
            result[0] += "Detalle de errores:"
            for error in errores[:3]:
                result[0] += f"""
Fila: {error['fila']}\nError: {error['error']}
Datos: {error['datos']}\n
"""
        result.append({
            'exitosos': exitosos,
            'errores': len(errores)
            })

    return result

def populate_clientes(csv_path: str):
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        exitosos = 0
        errores = []

        for num_fila, row in enumerate(csv_reader, 2):
            try:
                data = {
                    'idCliente': UUID(row['idCliente']),
                    'nombre': row['nombre'],
                    'correo': row['correo'],
                    'telefono': row['telefono'],
                    'estadoCuenta': row['estadoCuenta'],
                    'idEmpresa': UUID(row['idEmpresa'])
                }
                
                MongoModel.insertar_cliente(data)

                exitosos += 1
                
            except Exception as e:
                errores.append({
                    'fila': num_fila,
                    'error': str(e),
                    'datos': row
                })

        result = []
        result.append(f"""
\nResultado de la importación de Clientes:
• Registros exitosos: {exitosos}
• Errores: {len(errores)}

""")
        
        if errores:
            result[0] += "Detalle de errores:"
            for error in errores[:3]:
                result[0] += f"""
Fila: {error['fila']}\nError: {error['error']}
Datos: {error['datos']}\n
"""
        result.append({
            'exitosos': exitosos,
            'errores': len(errores)
            })

    return result

def populate_tickets(csv_path: str):
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        exitosos = 0
        errores = []

        for num_fila, row in enumerate(csv_reader, 2):
            try:
                data = {
                    'idTicket': UUID(row['idTicket']),
                    'idCliente': UUID(row['idCliente']),
                    'idAgente': UUID(row['idAgente']) if row['idAgente'] else None,
                    'idEmpresa': UUID(row['idEmpresa']),
                    'fechaCreacion': datetime.strptime(
                        row['fechaCreacion'],
                        '%Y-%m-%dT%H:%M:%S'
                    ),
                    'fechaCierre': datetime.strptime(
                        row['fechaCierre'],
                        '%Y-%m-%dT%H:%M:%S'
                    ) if row['fechaCierre'] else None,
                    'comentarios': ast.literal_eval(row['comentarios']) if row['comentarios'] else [],
                    'estado': int(row['estado']),
                    'prioridad': int(row['prioridad'])
                }
                
                MongoModel.insertar_ticket(data)

                exitosos += 1
                
            except Exception as e:
                errores.append({
                    'fila': num_fila,
                    'error': str(e),
                    'datos': row
                })

        result = []
        result.append(f"""
\nResultado de la importación de Tickets:
• Registros exitosos: {exitosos}
• Errores: {len(errores)}

""")
        
        if errores:
            result[0] += "Detalle de errores:"
            for error in errores[:3]:
                result[0] += f"""
Fila: {error['fila']}\nError: {error['error']}
Datos: {error['datos']}\n
"""
        result.append({
            'exitosos': exitosos,
            'errores': len(errores)
            })

    return result

def populate_all(csv_path):
    """
    Esta función carga datos desde archivos CSV específicos ubicados en el directorio `csv_path`.

    Se espera que dentro de `csv_path` existan los siguientes archivos con estos nombres exactos:
    - `agentes.csv`
    - `empresas.csv`
    - `clientes.csv`
    - `tickets.csv`

    Si alguno de estos archivos no está presente, la función podría generar errores.
    """
    result = {}
    try:
        result['empresas'] = (populate_empresas(csv_path + 'empresas.csv'))
        result['agentes'] = (populate_agentes(csv_path + 'agentes.csv'))
        result['clientes'] = (populate_clientes(csv_path + 'clientes.csv'))
        result['tickets'] = (populate_tickets(csv_path + 'tickets.csv'))

        result['resumen'] = f"""
Resultado populate Mongo:
Agentes:
{result['agentes'][1]}
Empresas:
{result['empresas'][1]}
Clientes:
{result['clientes'][1]}
Tickets:
{result['tickets'][1]}
"""
        return result
    except FileNotFoundError as e:
        raise FileNotFoundError(f"{str(e)}\nAsegurarse que los archivos agentes, empresas, clientes y tickets en formato csv estén presentes dentro del path")
