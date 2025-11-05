import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from logi import logger
from CONFIG import AdParserConfig


class PageParser:
    def __init__(self, config):
        self.config = config or AdParserConfig
        self.driver = None
        self.setup_driver()

        self.common_ad_sizes = {
            (300, 250),
            (336, 280), 
            (728, 90),  
            (300, 600), 
            (300, 599), 
            (300, 598), 
            (320, 100),  
            (320, 50),   
            (970, 90),    
            (250, 250),  
            (200, 200),   
            (120, 600),
            (160, 600),   
            (1440, 140),
            (1380, 250),
            (1380, 120),
            (1380, 105),
        }
    #Инициализация драйвера
    def setup_driver(self):
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
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
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
    #Загрузка страницы с поддержкой JavaScript
    def load_page(self, url) -> bool:
        try:
            logger.info(f"Загрузка страницы: {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            logger.info(f"Страница успешно загружена: {url}")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки страницы {url}: {e}")
            return False
    #Обнаруживание рекламы на сайте
    def detect_ads(self):
        ads = []
        try:
            for selector in self.config.AD_SELECTORS:

                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                for element in elements:
                    
                    try:
                        
                        location = element.location
                        size = element.size

                        if size['height'] and size['width'] != 0:
                            result = [
                                {
                            'element': element.id,
                            'tag': element.tag_name,
                            'classes': element.get_attribute('class'),
                            'id': element.get_attribute('id'),
                            'location': location,
                            'size': size,
                            'is_displayed': element.is_displayed()
                            }]

                        
                    except Exception as e:
                        logger.error(f"Ошибка извлечения данных элемента: {e}")
                        return {}
                    
                    ads.extend(result)
                
        except Exception as e:
            logger.error(f"Ошибка при обнаружении рекламы: {e}")
        
        return ads
    



    
    #Закрывание драйвера
    def close(self):
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver закрыт")

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
