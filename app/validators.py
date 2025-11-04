import re
from urllib.parse import urlparse
from typing import List, Optional
from logger import logger

class URLValidator:
    """Валидатор URL"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:
            logger.warning(f"Invalid URL {url}: {e}")
            return False
    
    @staticmethod
    def normalize_urls(urls: List[str]) -> List[str]:
        """Нормализация списка URL"""
        valid_urls = []
        for url in urls:
            if URLValidator.is_valid_url(url):
                # Добавляем схему если отсутствует
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                valid_urls.append(url)
            else:
                logger.warning(f"Skipping invalid URL: {url}")
        
        return valid_urls
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Извлечение домена из URL"""
        try:
            return urlparse(url).netloc
        except Exception:
            return None