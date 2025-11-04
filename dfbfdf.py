from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class WebPageParser:
    def __init__(self):
        """Инициализация драйвера браузера с настройками"""
        self.options = Options()
        #self.options.add_argument("--headless")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--no-sandbox")

        
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 15)

    def load_page(self, url):
        """Загрузка страницы с прокруткой для активации динамического контента"""
        try:
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return True
        
        except Exception as e:
            print(f"Ошибка загрузки страницы: {e}")
            return False


    def analyze_dom_structure(self):
        """Анализ DOM-структуры для выявления потенциальных рекламных контейнеров"""
        suspicious_elements = []
        
        # Поиск элементов с характерными для рекламы атрибутами
        ad_indicators = [
            "div.banner__content",
        ]
        
        for indicator in ad_indicators:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)

                suspicious_elements += elements

            except:
                continue
                
        return list(set(suspicious_elements))

    def detect_ad_by_size(self, element):
        """Обнаружение рекламы по характерным размерам"""
        try:
            size = element.size
            width, height = size['width'], size['height']
            
            # Стандартные рекламные размеры (IAB)
            ad_sizes = [
                (300, 600),
                (600, 300),
                (1440, 140),
                (1380, 250),
                (1380, 120),
                (1380, 105),
                (1245, 120),
                (1205, 120),
                (1205, 250),

            ]
            
            return (width, height) in ad_sizes
        except:
            return False


    def detect_ads(self):
        """Основная функция обнаружения рекламных элементов"""
        ads_found = []
        
        # Поиск по DOM-структуре
        dom_ads = self.analyze_dom_structure()
        for element in dom_ads:
            if element.size['height'] and element.size['width'] != 0:
                if self.detect_ad_by_size(element):
                    ads_found.append({
                        'element': element,
                        'location': element.location,
                        'size': element.size
                    })
        
        return ads_found

    def get_page_metrics(self):
        """Сбор метрик страницы для анализа"""
        try:
            metrics = {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'ads_count': len(self.detect_ads())
            }
            return metrics
        except Exception as e:
            print(f"Ошибка сбора метрик: {e}")
            return {}

    def close(self):
        """Закрытие драйвера"""
        self.driver.quit()

# Пример использования
if __name__ == "__main__":
    parser = WebPageParser()
    
    if parser.load_page("https://ria.ru/"):  
        # Поиск рекламы
        ads = parser.detect_ads()
        for ad in ads:
            print(ad['size'])
        
        # Вывод метрик
        metrics = parser.get_page_metrics()
        print(f"Ссылка страницы: {metrics['url']}")
        print(f"Заголовок страницы: {metrics['title']}")
        print(f"Найдено рекламных элементов: {metrics['ads_count']}")
    
    #parser.close()