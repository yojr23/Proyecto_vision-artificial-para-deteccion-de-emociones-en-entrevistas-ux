import sys
import logging
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import QApplication  # Añadido para manejar la GUI
from ui.app import App

def setup_logging(debug: bool = False) -> None:
    """Configura logging con archivo y consola."""
    log_level = logging.DEBUG if debug else logging.INFO
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    logging.info(f"Logging inicializado (nivel={logging.getLevelName(log_level)})")
    logging.info(f"Archivo de log: {log_file}")

def ensure_directories(salida_dir: Path | str) -> None:
    """Crea los directorios base requeridos para la aplicación."""
    base_path = Path(salida_dir)
    directories = [
        base_path / "videos_originales",
        base_path / "fragmentos",
        base_path / "marcas",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Directorio asegurado: {directory}")

def main() -> None:
    # Detectar si se pasó --debug como argumento
    debug_mode = "--debug" in sys.argv
    setup_logging(debug=debug_mode)

    logging.info("  ndo el programa...")
    logging.info(f"Fecha y hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ensure_directories("data")

    # Inicializar la aplicación Qt
    app = QApplication(sys.argv)
    
    try:
        # Lanzar la GUI
        window = App(logger=logging.getLogger(__name__))  # Pasar el logger
        window.show()
        logging.info("Interfaz gráfica lanzada exitosamente")
        sys.exit(app.exec())  # Mantener la aplicación en ejecución
    except Exception as e:
        logging.exception("Error fatal en la aplicación: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()