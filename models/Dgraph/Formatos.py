# Formatos.py
import json
from typing import Dict, Any
import webbrowser
from models.Utils.dictionaries import tipoProblema

class Formatos:
    @staticmethod
    def _encabezado(titulo: str, ancho: int = 90) -> str:
        """Genera un encabezado consistente"""
        iguales = (ancho - len(titulo) - 2)
        return f"\n{'='*(iguales//2)} {titulo} {'='*(iguales//2)}\n"

    @staticmethod
    def _divisor(ancho: int = 90) -> str:
        """Genera un divisor visual"""
        return '-' * ancho

# 1. Agentes por empresa
    @staticmethod
    def agentes_empresa(data: Dict[str, Any]) -> str:
        """Formatea agentes por empresa"""
        empresa = data['empresa'][0]
        output = []
        
        output.append(Formatos._encabezado("REPORTE DE AGENTES"))
        output.append(f"📌 Empresa: {empresa.get('nombreEmpresa', 'N/A')} (ID: {empresa.get('idEmpresa', 'N/A')})")
        output.append(Formatos._divisor())
        output.append("🔹 Agentes:")
        
        for agente in empresa.get('TIENE', []):
            output.append(f"   - {agente.get('nombreAgente', 'N/A')} (ID: {agente.get('idAgente', 'N/A')})")
        
        output.append(Formatos._divisor())
        output.append(f"🔹 Total: {len(empresa.get('TIENE', []))} agentes")
        output.append("=" * 90)
        
        return '\n'.join(output)

# 2. Clientes por empresa
    @staticmethod
    def clientes_empresa(data: Dict[str, Any]) -> str:
        """Formatea clientes por empresa"""
        empresa = data['empresa'][0]
        output = []
        
        output.append(Formatos._encabezado("REPORTE DE CLIENTES"))
        output.append(f"🏢 Empresa: {empresa.get('nombreEmpresa', 'N/A')}")
        output.append(Formatos._divisor())
        output.append("🔹 Clientes:")
        
        for cliente in empresa.get('clientes', []):
            output.append(f"   - {cliente.get('nombreCliente', 'N/A')} (ID: {cliente.get('idCliente', 'N/A')})")
        
        output.append(Formatos._divisor())
        output.append(f"🔹 Total: {len(empresa.get('clientes', []))} clientes")
        output.append("=" * 90)
        
        return '\n'.join(output)

# 3. Cliente por ticket
    @staticmethod
    def clientes_ticket(data: Dict[str, Any]) -> str:
        """Cliente_por_ticket"""
        output = []
        if 'ticket' in data and len(data['ticket']) > 0:
            ticket = data['ticket'][0]
            cliente = ticket.get('~ABRE', [{}])[0] if ticket.get('~ABRE') else {}
            
            # Obtener código y descripción del tipo de problema
            codigo_problema = ticket.get('tipoProblema')
            if codigo_problema is not None:
                descripcion_problema = tipoProblema.get(codigo_problema, f"Desconocido ({codigo_problema})")
                problema_str = f"{codigo_problema} - {descripcion_problema}"  # Número + texto
            else:
                problema_str = "N/A"
            
            output.append(Formatos._encabezado("INFORMACIÓN DE TICKET"))
            output.append(f"🎫 Ticket ID: {ticket.get('idTicket', 'N/A')}")
            output.append(f"🔧 Tipo Problema: {problema_str}")  # Muestra Código - Descripción
            output.append(f"📝 Descripción: {ticket.get('descripcion', 'N/A')}")
            output.append(Formatos._divisor())
            
            output.append("👤 Cliente Asociado:")
            if cliente:
                output.append(f"   - Nombre: {cliente.get('nombreCliente', 'N/A')}")
                output.append(f"   - ID: {cliente.get('idCliente', 'N/A')}")
            else:
                output.append("   - No se encontró cliente asociado")
            
            output.append("=" * 90)
        else:
            output.append("ℹ️ No se encontró el ticket solicitado")
        
        return '\n'.join(output)

# 4. Tickets por empresa
    @staticmethod
    def tickets_empresa(data: Dict[str, Any]) -> str:
        output = []
        if 'empresa' in data and data['empresa']:
            empresa = data['empresa'][0]
            
            output.append(Formatos._encabezado("TICKETS REPORTE"))
            output.append(f"🏢 Empresa: {empresa.get('nombreEmpresa', 'N/A')}")
            output.append(Formatos._divisor())
            
            for ticket in empresa.get('~PERTENECE', []):
                # Obtener código y descripción del problema
                codigo_problema = ticket.get('tipoProblema')
                if codigo_problema is not None:
                    descripcion = tipoProblema.get(codigo_problema, f"Desconocido ({codigo_problema})")
                    problema_str = f"{codigo_problema} - {descripcion}"  # Formato "Código - Descripción"
                else:
                    problema_str = "N/A"
                
                output.extend([
                    f"🎫 Ticket ID: {ticket.get('idTicket', 'N/A')}",
                    f"📝 Descripción: {ticket.get('descripcion', 'N/A')}",
                    f"🔧 Tipo Problema: {problema_str}",  # Muestra código y texto
                    Formatos._divisor()
                ])
            
            output.append(f"🔍 Total tickets: {len(empresa.get('~PERTENECE', []))}")
        else:
            output.append("❌ No se encontraron datos de empresa")
        
        output.append("=" * 90)
        return '\n'.join(output)

# 5. Tickets por cliente
    @staticmethod
    def tickets_cliente(data: Dict[str, Any]) -> str:  # Elimina el parámetro tipo_problema
        """Tickets por cliente"""
        output = []
        
        if not data.get('cliente'):
            return "❌ No se encontraron datos del cliente"

        cliente = data['cliente'][0]
        output.append(Formatos._encabezado("TICKETS POR CLIENTE"))
        output.append(f"👤 Cliente: {cliente.get('nombreCliente', 'N/A')}")
        output.append(Formatos._divisor())

        tickets = cliente.get('ABRE', [])
        
        for ticket in tickets:
            codigo_problema = ticket.get('tipoProblema')
            if codigo_problema is not None:
                descripcion = tipoProblema.get(codigo_problema, f"Desconocido ({codigo_problema})")  # Usa el import directo
                problema_str = f"{codigo_problema} - {descripcion}"
            else:
                problema_str = "N/A"

            output.extend([
                f"🎫 Ticket ID: {ticket.get('idTicket', 'N/A')}",
                f"📝 Descripción: {ticket.get('descripcion', 'N/A')}",
                f"🔧 Tipo Problema: {problema_str}",
                Formatos._divisor()
            ])

        output.append(f"🔍 Total tickets: {len(tickets)}")
        output.append("=" * 90)
        return '\n'.join(output)

# 6. Agentes por ticket
    @staticmethod
    def agente_ticket(data: Dict[str, Any]) -> str:
        """Formatea la información de agentes asociados a un ticket"""
        output = []
        
        if 'ticket' in data and len(data['ticket']) > 0:
            ticket = data['ticket'][0]
            agentes = ticket.get('~SOLUCIONA', [])
            
            output.append(Formatos._encabezado("AGENTES ASIGNADOS AL TICKET"))
            output.append(f"🎫 Ticket ID: {ticket.get('idTicket', 'N/A')}")
            output.append(Formatos._divisor())
            
            if agentes:
                output.append("🔧 Agentes asignados:")
                for agente in agentes:
                    output.append(f"   - {agente.get('nombreAgente', 'N/A')} (ID: {agente.get('idAgente', 'N/A')})")
            else:
                output.append("⚠️ No hay agentes asignados a este ticket")
            
            output.append("=" * 90)
        else:
            output.append("❌ No se encontró el ticket solicitado")
        
        return '\n'.join(output)

# 7. Tickets de agente de una empresa por tipo de problema.
    @staticmethod
    def tickets_empresa_tipo(data: Dict[str, Any]) -> str:
        """Formatea tickets filtrados por empresa mostrando código y descripción del problema"""
        output = []
        
        if 'empresa' in data and len(data['empresa']) > 0:
            empresa = data['empresa'][0]
            tickets = empresa.get('~PERTENECE', [])
            
            output.append(Formatos._encabezado("TICKETS POR TIPO DE PROBLEMA"))
            output.append(f"🏢 Empresa: {empresa.get('nombreEmpresa', 'N/A')}")
            
            # Obtener y formatear el tipo de problema principal
            tipo_problema_cod = tickets[0].get('tipoProblema') if tickets else None
            if tipo_problema_cod is not None:
                problema_desc = tipoProblema.get(tipo_problema_cod, f"Desconocido ({tipo_problema_cod})")
                output.append(f"🔧 Tipo de Problema: {tipo_problema_cod} - {problema_desc}")
            else:
                output.append("🔧 Tipo de Problema: N/A")
            
            output.append(Formatos._divisor())
            
            if tickets:
                output.append("🎫 Tickets encontrados:")
                for ticket in tickets:
                    # Formatear tipo de problema para cada ticket
                    ticket_problema_cod = ticket.get('tipoProblema')
                    if ticket_problema_cod is not None:
                        ticket_problema_desc = tipoProblema.get(ticket_problema_cod, f"Desconocido ({ticket_problema_cod})")
                        problema_str = f"{ticket_problema_cod} - {ticket_problema_desc}"
                    else:
                        problema_str = "N/A"
                    
                    output.extend([
                        f"\n  • ID: {ticket.get('idTicket', 'N/A')}",
                        f"  📝 Descripción: {ticket.get('descripcion', 'N/A')}",
                        f"  🔧 Tipo: {problema_str}",
                        Formatos._divisor(60)
                    ])
                output.append(f"🔍 Total tickets: {len(tickets)}")
            else:
                output.append("ℹ️ No se encontraron tickets para este tipo de problema")
            
            output.append("=" * 90)
        else:
            output.append("❌ No se encontró la empresa o no hay datos")
        
        return '\n'.join(output)

# 8. Tickets de agente por tipo de problema.
    @staticmethod
    def tickets_agente_tipo(data: Dict[str, Any]) -> str:
        """Formatea tickets filtrados por agente mostrando código y descripción del problema"""
        output = []
        
        if 'agente' in data and len(data['agente']) > 0:
            agente = data['agente'][0]
            tickets = agente.get('SOLUCIONA', [])
            
            output.append(Formatos._encabezado("TICKETS POR TIPO DE PROBLEMA"))
            output.append(f"👤 agente: {agente.get('nombreAgente', 'N/A')}")
            
            # Obtener y formatear el tipo de problema principal
            tipo_problema_cod = tickets[0].get('tipoProblema') if tickets else None
            if tipo_problema_cod is not None:
                problema_desc = tipoProblema.get(tipo_problema_cod, f"Desconocido ({tipo_problema_cod})")
                output.append(f"🔧 Tipo de Problema: {tipo_problema_cod} - {problema_desc}")
            else:
                output.append("🔧 Tipo de Problema: N/A")
            
            output.append(Formatos._divisor())
            
            if tickets:
                output.append("🎫 Tickets encontrados:")
                for ticket in tickets:
                    # Formatear tipo de problema para cada ticket
                    ticket_problema_cod = ticket.get('tipoProblema')
                    if ticket_problema_cod is not None:
                        ticket_problema_desc = tipoProblema.get(ticket_problema_cod, f"Desconocido ({ticket_problema_cod})")
                        problema_str = f"{ticket_problema_cod} - {ticket_problema_desc}"
                    else:
                        problema_str = "N/A"
                    
                    output.extend([
                        f"\n  • ID: {ticket.get('idTicket', 'N/A')}",
                        f"  📝 Descripción: {ticket.get('descripcion', 'N/A')}",
                        f"  🔧 Tipo: {problema_str}",
                        Formatos._divisor(60)
                    ])
                output.append(f"🔍 Total tickets: {len(tickets)}")
            else:
                output.append("ℹ️ No se encontraron tickets para este tipo de problema")
            
            output.append("=" * 90)
        else:
            output.append("❌ No se encontró la empresa o no hay datos")
        
        return '\n'.join(output)

# 9. Búsqueda de Ticket por Agente y Empresa por medio de palabras clave.
    @staticmethod
    def tickets_agente_empresa_palabras(data: Dict[str, Any]) -> str:
        """Formatea tickets encontrados por agente, empresa y palabras clave con descripciones completas"""
        output = []
        
        if 'empresa' in data and len(data['empresa']) > 0:
            empresa = data['empresa'][0]
            agentes = empresa.get('TIENE', [])
            
            output.append(Formatos._encabezado("TICKETS POR AGENTE Y PALABRAS CLAVE"))
            output.append(f"🏢 Empresa: {empresa.get('nombreEmpresa', 'N/A')}")
            output.append(Formatos._divisor())
            
            if agentes:
                agente = agentes[0]  # Debería ser único por el filtro de ID
                tickets = agente.get('SOLUCIONA', [])
                
                output.append(f"👤 Agente: {agente.get('nombreAgente', 'N/A')} (ID: {agente.get('idAgente', 'N/A')})")
                output.append(Formatos._divisor())
                
                if tickets:
                    output.append("🔍 Tickets encontrados:")
                    for ticket in tickets:
                        # Formatear tipo de problema con código y descripción
                        codigo_problema = ticket.get('tipoProblema')
                        if codigo_problema is not None:
                            desc_problema = tipoProblema.get(codigo_problema, f"Desconocido ({codigo_problema})")
                            problema_str = f"{codigo_problema} - {desc_problema}"
                        else:
                            problema_str = "N/A"
                        
                        # Formatear prioridad si existe
                        prioridad = ticket.get('prioridad')
                        prioridad_str = f"{prioridad} - {prioridad.get(prioridad, 'N/A')}" if prioridad else "N/A"
                        
                        output.extend([
                            f"\n  • ID: {ticket.get('idTicket', 'N/A')}",
                            f"  📝 Descripción: {ticket.get('descripcion', 'N/A')}",
                            f"  🔧 Tipo Problema: {problema_str}",
                            f"  🚦 Prioridad: {prioridad_str}",
                            f"  📌 Estado: {ticket.get('estado', 'N/A')}",
                            Formatos._divisor(60)
                        ])
                    output.append(f"🔍 Total tickets encontrados: {len(tickets)}")
                else:
                    output.append("ℹ️   No se encontraron tickets con las palabras clave para este agente")
            else:
                output.append("⚠️ Agente no encontrado en esta empresa")
            
            output.append("=" * 90)
        else:
            output.append("❌ Empresa no encontrada")
        
        return '\n'.join(output)

# 10. Dirección de la empresa por medio de su ID.

    @staticmethod
    def direccion_empresa(data: Dict[str, Any]) -> str:
        """Formatea la información de ubicación de la empresa con enlace a Google Maps"""
        output = []
        
        if 'empresa' in data and len(data['empresa']) > 0:
            empresa = data['empresa'][0]
            ubicacion = empresa.get('ubicacion', {})
            coords = ubicacion.get('coordinates', [])
            
            output.append(Formatos._encabezado("UBICACIÓN DE EMPRESA"))
            output.append(f"🏢 Empresa: {empresa.get('nombreEmpresa', 'N/A')}")
            output.append(Formatos._divisor())
            
            if coords and len(coords) >= 2:
                lon, lat = coords[0], coords[1]
                google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                
                output.append("📍 Coordenadas:")
                output.append(f"  - Latitud: {lat}")
                output.append(f"  - Longitud: {lon}")
                output.append(Formatos._divisor())
                output.append("🗺️ Enlace a Google Maps:")
                output.append(f"  {google_maps_link}")
                # Abre el enlace en el navegador
                webbrowser.open_new_tab(google_maps_link)
            else:
                output.append("⚠️ No hay datos de ubicación disponibles")
            
            output.append("=" * 90)
        else:
            output.append("❌ No se encontró la empresa especificada")
        
        return '\n'.join(output)

def print_formatted(res, formato: str):
    """Imprime los datos formateados"""
    try:
        parsed = json.loads(res.json)
        formatter = getattr(Formatos, formato.lower().replace(" ", "_"), None)
        
        if formatter:
            print(formatter(parsed))
        else:
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error al formatear: {str(e)}")
        print("Salida cruda:")
        print(json.dumps(parsed, indent=2))