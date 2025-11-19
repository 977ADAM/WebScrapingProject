import sys
import os
from ADPARSER import AdParser
from LOGI import logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    BASE_URLS = ["https://www.m24.ru/"]
    
    parser = AdParser()

    try:
        logger.info("Запуск парсинга рекламных элементов...")
        results = parser.parse_urls(BASE_URLS)

        successful = sum(1 for r in results if r.get('success'))
        total_ads = sum(r.get('ads_count', 0) for r in results)

        logger.info(f"Парсинг завершен!")
        logger.info(f"Успешно обработано: {successful}/{len(BASE_URLS)}")
        logger.info(f"Всего найдено рекламных элементов: {total_ads}")

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())