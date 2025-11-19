import os
import re
import json
from datetime import datetime
from PAGEPARSER import PageParser
from VALIDATOR import URLValidator
from LOGI import logger

class AdParser:
    def __init__(self):
        self.validator = URLValidator()
        self.base_reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
        self.ensure_directories()
        self.result = []
        

    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.base_reports_dir, exist_ok=True)

    def parse_urls(self, urls):
        valid_urls = self.validator.normalize_urls(urls)
        logger.info(f"Начинаем обработку {len(valid_urls)} валидных URL")
        results = []


        for url in valid_urls:
            try:
                path = self.folder_reporst(url)

                result = self.parse_single_url(url, path)

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

    def parse_single_url(self, url, base_path):
        logger.info(f"Начинаем парсинг: {url}")
        result = {
            'url': url,
            'domain': self.validator.extract_domain(url),
            'success': False,
            'ads_count': 0,
            'ads': [],
            'ads_click': [],
        }
        with PageParser() as parser:
            if not parser.load_page(url):
                result['error'] = 'Failed to load page'
                return result
            
            parser.get_cookies(base_path)
            elements = parser.elements()

            selenium_ads = parser.detect_ads(elements)
            parser.screenshots(elements, base_path)
            #result_click_elements = parser.click_elements(elements)
            
            #result['ads_click'] = result_click_elements
            result['ads'] = selenium_ads
            result['ads_count'] = len(selenium_ads)
            result['success'] = True
            
            logger.info(f"Парсинг завершен: {url} - найдено {len(selenium_ads)} рекламных элементов")

        self.result = result
        self.generate_report(base_path)

        return result

    def generate_report(self, base_path):
        """Генерация отчета"""
        if not self.result:
            logger.warning("Нет данных для отчета")
            return ""

        data_dir = os.path.join(base_path, "data")
        os.makedirs(data_dir, exist_ok=True)

        return self._generate_json_report(data_dir)

    def _generate_json_report(self, report_dir):
        """Генерация JSON отчета"""
        filename = os.path.join(report_dir, "ad_report.json")
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'results': self.result
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON отчет сохранен: {filename}")
        return filename
     
    def folder_reporst(self, url):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        domain = self.validator.extract_domain(url) or "unknown"
        domain_clean = self.sanitize_filename(domain)
        url_folder = os.path.join(self.base_reports_dir, domain_clean)
        os.makedirs(url_folder, exist_ok=True)

        name_timestamp = f"{domain_clean}_{timestamp}"
        url_folder_timestamp = os.path.join(url_folder, name_timestamp)
        os.makedirs(url_folder_timestamp, exist_ok=True)

        return url_folder_timestamp
    
    def sanitize_filename(self, name):
        """Очистка строки для использования в имени файла/папки"""
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        sanitized = sanitized.strip(' .')
        return sanitized[:100]