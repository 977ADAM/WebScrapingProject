import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from logger import logger
from default_config import AdParserConfig
from page_parser import PageParser

class AdDetector:
    """Модуль обнаружения рекламных элементов"""
    
    def __init__(self, config: AdParserConfig = None):
        self.config = config or AdParserConfig()
        self.detected_ads = []
        self.import_driver = PageParser(self.config)
    
    def _is_ad_element(self, element: Tag) -> bool:
        """Проверка, является ли элемент рекламным"""
        # Проверка атрибутов
        attrs = str(element.attrs).lower()
        ad_keywords = ['ad', 'banner', 'ads', 'adv', 'advertisement']
        
        return any(keyword in attrs for keyword in ad_keywords)
    
    def _extract_ad_data(self, element: Tag, detection_method: str) -> Dict[str, Any]:
        """Извлечение данных об рекламном элементе"""
        return {
            'tag': element.name,
            'classes': element.get('class', []),
            'id': element.get('id'),
            'attributes': dict(element.attrs),
            'detection_method': detection_method,
            'text_preview': element.get_text(strip=True)[:100] if element.get_text(strip=True) else '',
            'position': self._estimate_element_position(element)
        }
    
    def _estimate_element_position(self, element: Tag) -> Dict[str, Any]:
        """Оценка позиции элемента (упрощенная)"""
        # В реальной реализации нужно получить реальные координаты через Selenium
        return {
            'estimated_method': 'dom_order',
            'note': 'Real coordinates require WebElement access'
        }
    
    def _remove_duplicate_ads(self, ads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Удаление дублирующихся рекламных элементов"""
        seen = set()
        unique_ads = []
        
        for ad in ads:
            # Создаем ключ для идентификации дубликатов
            ad_key = (
                ad.get('tag'),
                tuple(ad.get('classes', [])),
                ad.get('id'),
                ad.get('detection_method')
            )
            
            if ad_key not in seen:
                seen.add(ad_key)
                unique_ads.append(ad)
        
        return unique_ads
    

    
    def _extract_selenium_ad_data(self, element: WebElement, detection_method: str) -> Dict[str, Any]:
        """Извлечение данных из Selenium элемента"""
        try:
            location = element.location
            size = element.size
            
            return {
                'tag': element.tag_name,
                'classes': element.get_attribute('class'),
                'id': element.get_attribute('id'),
                'detection_method': detection_method,
                'location': location,
                'size': size,
                'is_displayed': element.is_displayed(),
                'text_preview': element.text[:100] if element.text else ''
            }
        except Exception as e:
            logger.error(f"Ошибка извлечения данных элемента: {e}")
            return {}
    
    def _detect_by_element_size(self) -> List[Dict[str, Any]]:
        """Обнаружение рекламы по стандартным размерам"""
        ads = []
        
        try:
            all_elements = self.import_driver.driver.find_elements(By.CSS_SELECTOR, 'div, iframe, img')
            
            for element in all_elements:
                try:
                    if not element.is_displayed():
                        continue
                    
                    size = element.size
                    element_size = (size['width'], size['height'])
                    
                    # Проверяем соответствие стандартным размерам рекламы
                    if element_size in self.config.STANDARD_AD_SIZES:
                        ad_data = self._extract_selenium_ad_data(element, "standard_size")
                        ad_data['matched_size'] = element_size
                        ads.append(ad_data)
                        
                except Exception as e:
                    continue  # Пропускаем элементы, которые стали недоступны
                    
        except Exception as e:
            logger.error(f"Ошибка при обнаружении по размерам: {e}")
        
        return ads