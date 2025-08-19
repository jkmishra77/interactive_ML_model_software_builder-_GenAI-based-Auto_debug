# utils/logger.py
import logging

def setup_logger(name: str, level=logging.ERROR) -> logging.Logger:
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    return logging.getLogger(name)

