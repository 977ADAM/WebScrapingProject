from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image, ImageDraw
from fake_useragent import UserAgent
import time

class PageParser:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(f"--user-agent={UserAgent().random}")
        self.driver = webdriver.Chrome(options=chrome_options)

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
    
    def load_page(self, timeout=10):
        """Загрузка страницы с ожиданием полной инициализации"""
        self.driver.get("https://ria.ru/")
        time.sleep(20)
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def find_ad_elements(self):
        """Обнаружение элементов с рекламными размерами"""
        ad_elements = []
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.banner')
        print(elements)
        for element in elements:
            print(element)
            try:
                    size = (element.size['width'], element.size['height'])
                    print(size)
                    

                    ad_elements.append({
                            'element': element,
                            'size': size,
                            'tag': element.tag_name,
                            'tag_name': element.tag_name,
                            'text': element.text[:100] + "..." if len(element.text) > 100 else element.text,
                            'classes': element.get_attribute("class"),
                            'id': element.get_attribute("id"),
                            'src': element.get_attribute("src"),
                            'href': element.get_attribute("href"),
                            'width': size['width'],
                            'height': size['height'],
                            'location': element.location
                        })
                    print(ad_elements)
            except Exception:
                continue
        return ad_elements
    
    def close(self):
        """Закрытие браузера"""
        self.driver.quit()
    
if __name__ == "__main__":
    parser = PageParser()
    
    try:
        # Анализ нескольких сайтов

        parser.load_page()
        parser.find_ad_elements()


            
    finally:
        parser.close()
    