import os
import time
from CONFIG import AdParserConfig
from datetime import datetime
from PAGEPARSER import PageParser
from validator import URLValidator
from report_manager import ReportManager
from my_logger import get_logger
logger = get_logger()

class AdParser:
    def __init__(self, config):
        self.config = config or AdParserConfig()
        self.validator = URLValidator()
        self.report_manager = ReportManager(self.config)
        self.results = []

    def parse_urls(self, urls):
        valid_urls = self.validator.normalize_urls(urls)
        logger.info(f"Начинаем обработку {len(valid_urls)} валидных URL")
        results = []


        for url in valid_urls:
            try:
                result = self.parse_single_url(url)

                folder_path = self.report_manager.create_url_folder(url)
                self.report_manager.generate_report(result, folder_path)

                results.append(result)

            except Exception as e:
                logger.error(f"Ошибка обработки URL {url}: {e}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results

    def parse_single_url(self, url):
        logger.info(f"Начинаем парсинг: {url}")
        result = {
            'url': url,
            'domain': self.validator.extract_domain(url),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'ads_count': 0,
            'ads': [],
            'ads_click': [],
        }
        with PageParser(self.config) as parser:
            if not parser.load_page(url):
                result['error'] = 'Failed to load page'
                return result
            elements = parser.elements()

            selenium_ads = parser.detect_ads(elements)
            parser.screenshots(elements)
            #result_click_elements = parser.click_elements(elements)
            
            #result['ads_click'] = result_click_elements
            result['ads'] = selenium_ads
            result['ads_count'] = len(selenium_ads)
            result['success'] = True
            
            logger.info(f"Парсинг завершен: {url} - найдено {len(selenium_ads)} рекламных элементов")
        
        return result
