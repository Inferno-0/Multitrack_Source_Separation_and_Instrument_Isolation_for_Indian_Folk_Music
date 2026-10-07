import logging
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def setup_logging(log_filename: str, generate_log: bool = True) -> logging.Logger:
    """
    Sets up the logger for the preprocessing package.
    Logs to a file and to stdout.
    
    Args:
        log_filename (str): Name of the log file.
        generate_log (bool): If True, write logs to file.
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("preprocessing")
    logger.setLevel(logging.INFO)
    logger.handlers = []

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    if generate_log:
        try:
            # Create a log path in the current working directory
            log_path = Path(log_filename)
            fh = logging.FileHandler(log_path, mode='a', encoding='utf-8')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")

    return logger

logger = logging.getLogger("preprocessing")
