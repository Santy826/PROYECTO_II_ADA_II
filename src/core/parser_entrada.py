"""Parsea el formato de entrada del enunciado."""

# concert_optimizer.py

def parse_input(text):
    """
    Parsea el texto de entrada con manejo robusto de errores
    
    Returns:
        tuple: (n, cities, error) 
               - Si OK: (n, cities, None)
               - Si falla: (None, None, mensaje_error)
    """
    try:
        lines = text.strip().split('\n')
        
        # Validar que haya suficientes líneas
        if len(lines) < 2:
            return None, None, "Entrada incompleta: se necesitan al menos 2 líneas"
        
        # Línea 1: N
        try:
            n = int(lines[0].strip())
        except ValueError:
            return None, None, f"Línea 1 inválida: '{lines[0]}' no es un número entero"
        
        # Línea 2: M
        try:
            m = int(lines[1].strip())
        except ValueError:
            return None, None, f"Línea 2 inválida: '{lines[1]}' no es un número entero"
        
        # Validar que haya suficientes líneas para las ciudades
        if len(lines) < 2 + m:
            return None, None, f"Se esperaban {m} ciudades pero solo hay {len(lines) - 2} líneas"
        
        # Líneas siguientes: ciudades
        cities = []
        for i in range(2, 2 + m):
            line = lines[i].strip()
            parts = line.split()
            
            # Validar formato de la línea
            if len(parts) < 3:
                return None, None, f"Línea {i+1} mal formada: '{line}' (esperado: Nombre X Y)"
            
            name = parts[0]
            
            # Validar X
            try:
                x = int(parts[1])
            except ValueError:
                return None, None, f"Línea {i+1}: '{parts[1]}' no es un número válido para X"
            
            # Validar Y
            try:
                y = int(parts[2])
            except ValueError:
                return None, None, f"Línea {i+1}: '{parts[2]}' no es un número válido para Y"
            
            cities.append((name, x, y))
        
        return n, cities, None
        
    except Exception as e:
        return None, None, f"Error inesperado al parsear: {str(e)}"


def validate_input(n, cities):
    """
    Valida que los datos sean correctos
    
    Returns:
        list: Lista de errores (vacía si todo OK)
    """
    errors = []
    
    # Validar N
    if n <= 0:
        errors.append(f"N debe ser positivo, recibido: {n}")
    
    if n > 1000:
        errors.append(f"N muy grande ({n}), máximo recomendado: 1000")
    
    # Validar que haya ciudades
    if len(cities) == 0:
        errors.append("Debe haber al menos una ciudad")
    
    if len(cities) > 100:
        errors.append(f"Demasiadas ciudades ({len(cities)}), máximo recomendado: 100")
    
    # Validar coordenadas
    for name, x, y in cities:
        if x < 0 or x > n:
            errors.append(f"Ciudad {name}: X={x} fuera de rango [0, {n}]")
        if y < 0 or y > n:
            errors.append(f"Ciudad {name}: Y={y} fuera de rango [0, {n}]")
    
    # Validar ciudades duplicadas (mismo nombre)
    names = [name for name, _, _ in cities]
    if len(names) != len(set(names)):
        duplicates = [n for n in names if names.count(n) > 1]
        errors.append(f"Nombres duplicados: {set(duplicates)}")
    
    # Validar ciudades en misma posición
    positions = [(x, y) for _, x, y in cities]
    if len(positions) != len(set(positions)):
        # Encontrar cuáles están duplicadas
        seen = set()
        duplicated = set()
        for name, x, y in cities:
            pos = (x, y)
            if pos in seen:
                duplicated.add(pos)
            seen.add(pos)
        errors.append(f"Ciudades en posición duplicada: {duplicated}")
    
    return errors


