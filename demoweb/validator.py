import re
from urllib.parse import urlparse
from typing import List, Optional
from LOGI import logger

class URLValidator:
    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:
            logger.warning(f"Invalid URL {url}: {e}")
            return False
    
    @staticmethod
    def normalize_urls(urls: List[str]) -> List[str]:
        valid_urls = []
        for url in urls:
            if URLValidator.is_valid_url(url):
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                valid_urls.append(url)
            else:
                logger.warning(f"Skipping invalid URL: {url}")
        
        return valid_urls
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        try:
            return urlparse(url).netloc
        except Exception:
            return None