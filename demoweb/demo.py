import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class PageParser:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
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
    

    def load_page(self, url, timeout=10):
        """Загрузка страницы с ожиданием полной инициализации"""
        self.driver.get(url)
        time.sleep(20)
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )


    def scroll(self):
        start_position = 0
        page_height = self.driver.execute_script("return document.body.scrollHeight")

        while start_position < page_height:
            # Прокручиваем небольшими шагами по 100 пикселей
            start_position += 200
            self.driver.execute_script(f"window.scrollTo(0, {start_position});")
            time.sleep(1)  # Задержка для плавности
            # Обновляем высоту страницы на случай динамической подгрузки
            page_height = self.driver.execute_script("return document.body.scrollHeight")


    def detect_ad_elements(self):
        """Обнаружение элементов с рекламными размерами"""
        ad_elements = []
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.banner')        
        for element in elements:
                try:
                    size = (element.size['width'], element.size['height'])
                    if size in self.common_ad_sizes:
                        
                        ad_elements.append({
                            'element': element,
                            'size': size,
                            'tag': element.tag_name,
                            'location': element.location,
                            'tag_name': element.tag_name,
                            'text': element.text[:100] + "..." if len(element.text) > 100 else element.text,
                            'classes': element.get_attribute("class"),
                            'id': element.get_attribute("id"),
                            'src': element.get_attribute("src"),
                            'href': element.get_attribute("href")
                        })
                except Exception:
                    continue
        return ad_elements
    

    def analyze_page(self, url):
        """Полный анализ страницы"""
        self.load_page(url)
        self.scroll()
        ads = self.detect_ad_elements()
        return {
            'url': url,
            'ads_count': len(ads),
            'ad_elements': ads
        }


    def close(self):
        """Закрытие браузера"""
        self.driver.quit()


    def run(self):
        
        parser = PageParser()
        try:
            result = parser.analyze_page("https://ria.ru/")
            
            print(f"Найдено рекламных элементов: {result['ads_count']}")
            for ad in result['ad_elements']:
                print(f"Размер: {ad['size']}")
                print(f"Тег: {ad['tag']}")
                print(f"Местоположение: {ad['location']}")
                print(f"Содержание блока: {ad['text']}")

                print('-' * 40)

        finally:
            parser.close()
