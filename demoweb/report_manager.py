import re
import os
import json
import csv
from datetime import datetime
from CONFIG import AdParserConfig
from validator import URLValidator
from my_logger import get_logger
logger = get_logger()

class ReportManager:
    def __init__(self, config):
        self.config = config or AdParserConfig()
        self.validator = URLValidator()
        self.base_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
        self.dict_directories = {}
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        directories = [
            "reports",
            "logs"
        ]
        for directorie in directories:

            directorie_path = os.path.join(self.base_output_dir, directorie)

            os.makedirs(directorie_path, exist_ok=True)

            self.dict_directories[directorie] = directorie_path

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

    def generate_report(self, result, folder_path):
        """Генерация отчета"""
        if not result:
            logger.warning("Нет данных для отчета")
            return ""
        
        data_dir = os.path.join(folder_path, "data")

        os.makedirs(data_dir, exist_ok=True)

        return self._generate_json_report(data_dir, result)

    def _generate_json_report(self, report_dir, result):
        """Генерация JSON отчета"""
        filename = f"{report_dir}/ad_report.json"
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_urls_processed': len(result),
            'results': result
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON отчет сохранен: {filename}")
        return filename

    def get_path_log(self):
        return self.dict_directories["logs"]