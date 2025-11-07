import os
import time
from LOGI import logger
from datetime import datetime
from PAGEPARSER import PageParser
import json

class AdParser:
    def __init__(self, config):
        self.config = config
        self.results = []
    #Здесь начинается парсинг всех ссылок на сайты.
    def parse_urls(self, urls):
        results = []
        
        for url in urls:
            try:
                result = self.parse_single_url(url)
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
    #Парсинг одной ссылки.
    def parse_single_url(self, url):

        logger.info(f"Начинаем парсинг: {url}")
        
        result = {
            'url': url,
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
            
            seen = set()
            data = parser.detect_ads()
            selenium_ads = []
            for d in data:
                if d['element'] not in seen:
                    seen.add(d['element'])
                    selenium_ads.append(d)
            
            parser.screenshots()

            parser.screenshot_full_page()
            
            result_click_elements = parser.click_elements()
            
            result['ads_click'] = result_click_elements
            result['ads'] = selenium_ads
            result['ads_count'] = len(selenium_ads)
            result['success'] = True
            
            logger.info(f"Парсинг завершен: {url} - найдено {len(selenium_ads)} рекламных элементов")
        
        return result
    #Создание отчета в нужном формате.
    def generate_report(self):
        """Генерация отчета"""
        if not self.results:
            logger.warning("Нет данных для отчета")
            return ""
        
        report_dir = "reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._generate_json_report(timestamp, report_dir)
    #Отчет в JSON формате
    def _generate_json_report(self, timestamp, report_dir):
        """Генерация JSON отчета"""
        filename = f"{report_dir}/ad_report_{timestamp}.json"
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_urls_processed': len(self.results),
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON отчет сохранен: {filename}")
        return filename