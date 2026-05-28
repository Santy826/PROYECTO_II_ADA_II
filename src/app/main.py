"""
main.py
-------
Punto de entrada de la aplicación "¿Dónde pongo mi concierto?".

Para ejecutar la aplicación desde la raíz del proyecto:
    python -m src.app.main
    
O directamente:
    python src/app/main.py
"""

import sys
import os

# Garantizar que Python encuentre el paquete 'src' sin importar
# desde dónde se ejecute el script.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.gui.ventana_principal import construir_ventana


def main() -> None:
    """Función principal: inicia la interfaz gráfica."""
    construir_ventana()


if __name__ == "__main__":
    main()
