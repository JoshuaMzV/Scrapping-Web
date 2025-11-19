"""
Utilidades generales para la aplicación
"""

def limpiar_precio(precio_str):
    """Limpia el string de precio y retorna float"""
    if not precio_str:
        return 0.0
    precio_str = precio_str.replace('$', '').replace(',', '.').replace('USD', '').replace('US', '').strip()
    try:
        return float(precio_str)
    except:
        return 0.0


def es_producto_con_tallas(nombre_producto):
    """
    Detecta si un producto debe incluir columna de tallas
    Basado en palabras clave en el nombre
    """
    from src.config import PALABRAS_CLAVE_CON_TALLAS, PALABRAS_CLAVE_SIN_TALLAS
    
    nombre_lower = nombre_producto.lower()
    
    # Primero revisar palabras clave de SIN tallas (prioridad alta)
    for palabra in PALABRAS_CLAVE_SIN_TALLAS:
        if palabra in nombre_lower:
            return False
    
    # Luego revisar palabras clave de CON tallas
    for palabra in PALABRAS_CLAVE_CON_TALLAS:
        if palabra in nombre_lower:
            return True
    
    # Por defecto, si tiene la palabra "talla" explícita, incluir
    if 'talla' in nombre_lower or 'size' in nombre_lower:
        return True
    
    return False
