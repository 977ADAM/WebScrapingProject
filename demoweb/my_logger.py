import logging
import sys
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class ColorFormatter(logging.Formatter):
    """Форматтер с цветным выводом для консоли"""
    
    FORMATS = {
        logging.DEBUG: f"{Colors.GRAY}%(asctime)s - %(name)s - DEBUG - %(message)s{Colors.RESET}",
        logging.INFO: f"{Colors.GREEN}%(asctime)s - %(name)s - INFO - %(message)s{Colors.RESET}",
        logging.WARNING: f"{Colors.YELLOW}%(asctime)s - %(name)s - WARNING - %(message)s{Colors.RESET}",
        logging.ERROR: f"{Colors.RED}%(asctime)s - %(name)s - ERROR - %(message)s{Colors.RESET}",
        logging.CRITICAL: f"{Colors.BOLD}{Colors.RED}%(asctime)s - %(name)s - CRITICAL - %(message)s{Colors.RESET}"
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

class SimpleLogger:
    def __init__(self, 
                 name: str = "ad_parser",
                 level: str = "INFO",
                 log_to_file: bool = True,
                 max_file_size: int = 10 * 1024 * 1024,  # 10 MB
                 backup_count: int = 5):
        
        self.name = name
        self.level = getattr(logging, level.upper())
        self.log_to_file = log_to_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Создаем логгер
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        self.logger.propagate = False
        
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Создаем обработчики
        self._setup_console_handler()
        if log_to_file:
            self._setup_file_handler()
    
    def _setup_console_handler(self):
        """Настройка обработчика для консоли"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(ColorFormatter())
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Настройка обработчика для файла с ротацией"""
        # Создаем директорию для логов
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Формируем путь к файлу лога
        log_file = log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Обработчик с ротацией
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.level)
        
        # Формат для файла (без цветов)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _log_with_caller(self, level: int, msg: str, *args, **kwargs):
        """Логирование с информацией о вызывающем коде"""
        import inspect
        
        # Получаем информацию о вызывающем коде
        frame = inspect.currentframe().f_back.f_back  # Два уровня назад
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name
        
        # Добавляем информацию о вызывающем коде
        enhanced_msg = f"[{filename}:{lineno} in {func_name}] {msg}"
        self.logger.log(level, enhanced_msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        self._log_with_caller(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self._log_with_caller(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self._log_with_caller(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self._log_with_caller(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self._log_with_caller(logging.CRITICAL, msg, *args, **kwargs)
    
    def success(self, msg: str, *args, **kwargs):
        """Кастомный уровень для успешных операций"""
        enhanced_msg = f"{Colors.GREEN}✓{Colors.RESET} {msg}"
        self._log_with_caller(logging.INFO, enhanced_msg, *args, **kwargs)
    
    def progress(self, msg: str, *args, **kwargs):
        """Кастомный уровень для прогресса"""
        enhanced_msg = f"{Colors.CYAN}→{Colors.RESET} {msg}"
        self._log_with_caller(logging.INFO, enhanced_msg, *args, **kwargs)
    
    def section(self, msg: str, *args, **kwargs):
        """Кастомный уровень для разделов"""
        border = "=" * 60
        enhanced_msg = f"\n{border}\n{Colors.BOLD}{msg}{Colors.RESET}\n{border}"
        self._log_with_caller(logging.INFO, enhanced_msg, *args, **kwargs)

# Глобальный экземпляр логгера
_logger_instance: Optional[SimpleLogger] = None

def setup_logger(name: str = "ad_parser", level: str = "INFO", log_to_file: bool = True) -> SimpleLogger:
    """Настройка глобального логгера"""
    global _logger_instance
    _logger_instance = SimpleLogger(name, level, log_to_file)
    return _logger_instance

def get_logger() -> SimpleLogger:
    """Получение глобального логгера"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = setup_logger()
    return _logger_instance

# Функции для удобного использования
def debug(msg: str, *args, **kwargs):
    get_logger().debug(msg, *args, **kwargs)

def info(msg: str, *args, **kwargs):
    get_logger().info(msg, *args, **kwargs)

def warning(msg: str, *args, **kwargs):
    get_logger().warning(msg, *args, **kwargs)

def error(msg: str, *args, **kwargs):
    get_logger().error(msg, *args, **kwargs)

def critical(msg: str, *args, **kwargs):
    get_logger().critical(msg, *args, **kwargs)

def success(msg: str, *args, **kwargs):
    get_logger().success(msg, *args, **kwargs)

def progress(msg: str, *args, **kwargs):
    get_logger().progress(msg, *args, **kwargs)

def section(msg: str, *args, **kwargs):
    get_logger().section(msg, *args, **kwargs)

# Декоратор для логирования вызовов функций
def log_function_call(level: str = "DEBUG"):
    """Декоратор для логирования вызовов функций и их результатов"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            func_name = func.__name__
            
            # Логируем вызов функции
            getattr(logger, level.lower())(f"Вызов функции: {func_name}")
            
            try:
                # Выполняем функцию
                result = func(*args, **kwargs)
                
                # Логируем успешное завершение
                getattr(logger, level.lower())(f"Функция {func_name} завершена успешно")
                return result
                
            except Exception as e:
                # Логируем ошибку
                logger.error(f"Ошибка в функции {func_name}: {str(e)}")
                raise
        
        return wrapper
    return decorator


class Timer:
    """Контекстный менеджер для измерения времени выполнения блока кода"""
    
    def __init__(self, operation: str = "Операция"):
        self.operation = operation
        self.start_time = None
        self.logger = get_logger()
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.progress(f"Начало: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.success(f"Завершено: {self.operation} за {duration:.2f} сек")
        else:
            self.logger.error(f"Прервано: {self.operation} после {duration:.2f} сек")
        
        return False  # Не подавляем исключения