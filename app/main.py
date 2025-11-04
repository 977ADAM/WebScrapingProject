import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ad_parser import AdParser
from default_config import AdParserConfig
from logger import logger

def main():
    """Основная функция"""
    
    # Пример URL для тестирования
    test_urls = [
        "https://ria.ru"
        # Добавьте свои URL для тестирования
    ]
    
    # Настройка конфигурации
    config = AdParserConfig(
        HEADLESS=True,
        PAGE_LOAD_TIMEOUT=20
    )
    
    # Создание парсера
    parser = AdParser(config)
    
    try:
        # Запуск парсинга
        logger.info("Запуск парсинга рекламных элементов...")  
        results = parser.parse_urls(test_urls)

        # Генерация отчетов
        logger.info("Генерация отчетов...")
        json_report = parser.generate_report('json')
        
        # Статистика
        successful = sum(1 for r in results if r.get('success'))
        total_ads = sum(r.get('ads_count', 0) for r in results)
        
        logger.info(f"Парсинг завершен!")
        logger.info(f"Успешно обработано: {successful}/{len(test_urls)}")
        logger.info(f"Всего найдено рекламных элементов: {total_ads}")
        logger.info(f"JSON отчет: {json_report}")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())