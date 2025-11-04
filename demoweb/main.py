from logi import logger
from demo import PageParser
from screenshot import ScreenshotManager


def main():
    BASE_URL = ["https://ria.ru/"]

    parser = PageParser()

    try:
        logger.info("Запуск парсинга рекламных элементов...")
        result = parser.run(BASE_URL)


        #logger.info("Запуск создания скриншота и выделения...")
        #screetshot.run_screen()












    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())