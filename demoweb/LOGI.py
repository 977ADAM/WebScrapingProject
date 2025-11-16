import logging
import colorlog
import sys
from datetime import datetime
import os


def setup_logger(name = "ad_parser"):
    """Настройка логгера для приложения"""
    script_path = os.path.abspath(__file__)
    dirname = os.path.dirname(script_path)
    log_dir = os.path.join(dirname, "logs")
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow', 
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white'
        }
    )
    
    # Обработчик для файла
    file_handler = logging.FileHandler(
        f"{log_dir}/ad_parser.log"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    #console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Глобальный логгер
logger = setup_logger()
