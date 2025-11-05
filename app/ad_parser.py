import json
import csv
from typing import List, Dict, Any
from datetime import datetime
import os

from page_parser import PageParser
from ad_detector import AdDetector
from logger import logger
from validators import URLValidator
from default_config import AdParserConfig

class AdParser:
    """Основной класс приложения для парсинга рекламы"""
    
    def __init__(self, config: AdParserConfig = None):
        self.config = config or AdParserConfig()
        self.validator = URLValidator()
        self.results = []
    
    def parse_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Пакетная обработка URL"""
        
        # Валидация URL
        valid_urls = self.validator.normalize_urls(urls)
        logger.info(f"Начинаем обработку {len(valid_urls)} валидных URL")
        
        results = []
        
        for url in valid_urls:
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
    
    def parse_single_url(self, url: str) -> Dict[str, Any]:
        """Обработка одиночного URL"""
        logger.info(f"Начинаем парсинг: {url}")
        
        result = {
            'url': url,
            'domain': self.validator.extract_domain(url),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'ads_count': 0,
            'ads': [],
            'size': []
        }
        
        with PageParser(self.config) as parser:
            # Загрузка страницы
            if not parser.load_page(url):
                result['error'] = 'Failed to load page'
                return result
            
            # Обнаружение рекламы через Selenium


            selenium_ads = parser.detect_ads_with_selenium()
            print(selenium_ads)
            # Объединение результатов
            all_ads = selenium_ads
            result['ads'] = all_ads
            result['ads_count'] = len(all_ads)
            result['success'] = True
            
            logger.info(f"Парсинг завершен: {url} - найдено {len(all_ads)} рекламных элементов")
        
        return result
    
    def generate_report(self, output_format: str = 'json') -> str:
        """Генерация отчета"""
        if not self.results:
            logger.warning("Нет данных для отчета")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == 'json':
            return self._generate_json_report(timestamp)
        else:
            logger.error(f"Неподдерживаемый формат: {output_format}")
            return ""
    
    def _generate_json_report(self, timestamp: str) -> str:
        """Генерация JSON отчета"""
        filename = f"ad_report_{timestamp}.json"
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_urls_processed': len(self.results),
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON отчет сохранен: {filename}")
        return filename