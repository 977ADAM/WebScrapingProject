import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
import urllib3
from urllib3.exceptions import HTTPError

from logger import logger
from default_config import AdParserConfig

class PageParser:
    """Модуль парсинга веб-страниц"""
    
    def __init__(self, config: AdParserConfig = None):
        self.config = config or AdParserConfig()
        self.driver: Optional[webdriver.Chrome] = None
        self.setup_driver()
    
    def setup_driver(self) -> None:
        """Настройка WebDriver"""
        try:
            chrome_options = Options()
            
            if self.config.HEADLESS:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument(f"--window-size={self.config.WINDOW_SIZE[0]},{self.config.WINDOW_SIZE[1]}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-images")  # Ускоряет загрузку
            chrome_options.add_argument("--disable-javascript")  # Можно включить позже для JS
            
            # Базовые настройки для избежания детектации
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Устанавливаем таймауты
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            self.driver.set_script_timeout(self.config.SCRIPT_TIMEOUT)
            
            logger.info("WebDriver успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации WebDriver: {e}")
            raise
    
    def load_page(self, url: str) -> bool:
        """Загрузка страницы по URL"""
        try:
            logger.info(f"Загрузка страницы: {url}")
            self.driver.get(url)
            
            # Ждем загрузки DOM
            WebDriverWait(self.driver, self.config.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Дополнительное время для загрузки динамического контента
            time.sleep(2)
            
            logger.info(f"Страница успешно загружена: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки страницы {url}: {e}")
            return False
    
    def detect_ads_with_selenium(self) -> List[Dict[str, Any]]:
        """Обнаружение рекламы с использованием Selenium WebDriver"""
        ads = []
        try:
            # Поиск по CSS селекторам через Selenium
            for selector in self.config.AD_SELECTORS:
                print(selector)
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    print(element)
                    try:
                        location = element.location
                        size = element.size
            
                        result = [
                            {
                        'tag': element.tag_name,
                        'classes': element.get_attribute('class'),
                        'id': element.get_attribute('id'),
                        'location': location,
                        'size': size,
                        'is_displayed': element.is_displayed(),
                        'text_preview': element.text[:100] if element.text else ''
                        }]
                        ads += result
                    except Exception as e:
                        logger.error(f"Ошибка извлечения данных элемента: {e}")
                        return {}
            
        except Exception as e:
            logger.error(f"Ошибка при обнаружении рекламы через Selenium: {e}")
        
        return ads

    def execute_script(self, script: str) -> Any:
        """Выполнение JavaScript на странице"""
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            logger.error(f"Ошибка выполнения скрипта: {e}")
            return None
    
    def switch_to_iframe(self, iframe_element) -> bool:
        """Переключение на iframe"""
        try:
            self.driver.switch_to.frame(iframe_element)
            return True
        except Exception as e:
            logger.error(f"Ошибка переключения на iframe: {e}")
            return False
    
    def switch_to_main_frame(self) -> None:
        """Возврат к основному фрейму"""
        self.driver.switch_to.default_content()
    
    def get_all_iframes(self):
        """Получение всех iframe элементов"""
        return self.driver.find_elements(By.TAG_NAME, "iframe")
    
    def close(self) -> None:
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver закрыт")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()