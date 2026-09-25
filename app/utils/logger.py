import logging
import sys
from pathlib import Path

def setup_logger(run_id: str, log_dir: str = "logs") -> logging.Logger:
    """Set up structured logging with file and console output."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(run_id)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler
    fh = logging.FileHandler(f"{log_dir}/{run_id}.log", encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger
