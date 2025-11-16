import os
import re
import json
from CONFIG import AdParserConfig
from datetime import datetime
from PAGEPARSER import PageParser
from VALIDATOR import URLValidator
from LOGI import logger

class AdParser:
    def __init__(self, config):
        self.config = config or AdParserConfig()
        self.validator = URLValidator()
        self.base_reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
        self.ensure_directories()
        self.results = []

    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.base_reports_dir, exist_ok=True)

    def parse_urls(self, urls):
        valid_urls = self.validator.normalize_urls(urls)
        logger.info(f"Начинаем обработку {len(valid_urls)} валидных URL")
        results = []


        for url in valid_urls:
            try:
                result = self.parse_single_url(url)

                path = self.folder_reporst(url)

                self.generate_report(path, result)

                results.append(result)

            except Exception as e:
                logger.error(f"Ошибка обработки URL {url}: {e}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        self.results = results
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

    def generate_report(self, base_path, result):
        """Генерация отчета"""
        if not result:
            logger.warning("Нет данных для отчета")
            return ""

        script_path = os.path.abspath(__file__)
        dirname = os.path.dirname(script_path)
        report_dir = os.path.join(dirname, "reports")
        os.makedirs(report_dir, exist_ok=True)

        data_dir = os.path.join(base_path, "data")
        os.makedirs(data_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._generate_json_report(timestamp, data_dir, result)

    def _generate_json_report(self, timestamp, report_dir, result):
        """Генерация JSON отчета"""
        filename = os.path.join(report_dir, "ad_report.json")
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'results': result
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON отчет сохранен: {filename}")
        return filename
     
    def folder_reporst(self, url):
        timestamp = datetime.now().strftime(self.config.FOLDER_TIMESTAMP_FORMAT)
        
        domain = self.validator.extract_domain(url) or "unknown"
        domain_clean = self.sanitize_filename(domain)
        url_folder = os.path.join(self.base_reports_dir, domain_clean)
        os.makedirs(url_folder, exist_ok=True)

        name_timestamp = f"{domain_clean}_{timestamp}"
        url_folder_timestamp = os.path.join(url_folder, name_timestamp)
        os.makedirs(url_folder_timestamp, exist_ok=True)

        return url_folder_timestamp



    def create_url_folder(self, url):
        """Создание папки для конкретного URL"""
        domain = self.validator.extract_domain(url) or "unknown"

        domain_clean = self.sanitize_filename(domain)
        
        url_folder = os.path.join(self.dict_directories["reports"], domain_clean)
        
        os.makedirs(url_folder, exist_ok=True)

        timestamp = datetime.now().strftime(self.config.FOLDER_TIMESTAMP_FORMAT)

        url_folder_timestamp = f"{url_folder}/{domain_clean}_{timestamp}"

        os.makedirs(url_folder_timestamp, exist_ok=True)

        logger.info(f"Создана папка для отчета: {url_folder_timestamp}")
        return url_folder_timestamp
    
    def sanitize_filename(self, name):
        """Очистка строки для использования в имени файла/папки"""
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        sanitized = sanitized.strip(' .')
        return sanitized[:100]