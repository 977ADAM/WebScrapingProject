import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from LOGI import logger
from ADPARSER import AdParser
from CONFIG import AdParserConfig



def main():
    BASE_URL = ["https://ria.ru",
                "https://tass.ru/",
                "https://secretmag.ru/",
                "https://www.m24.ru/",
                "https://1prime.ru/"
                ]

    config = AdParserConfig(HEADLESS=False)

    parser = AdParser(config)

    try:
        logger.info("Запуск парсинга рекламных элементов...")
        results = parser.parse_urls(BASE_URL)
        
        logger.info("Генерация отчета JSON")
        json_report = parser.generate_report()

        successful = sum(1 for r in results if r.get('success'))
        total_ads = sum(r.get('ads_count', 0) for r in results)

        logger.info(f"Парсинг завершен!")
        logger.info(f"Успешно обработано: {successful}/{len(BASE_URL)}")
        logger.info(f"Всего найдено рекламных элементов: {total_ads}")
        logger.info(f"JSON отчет: {json_report}")

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())