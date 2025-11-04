from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw
import time
from fake_useragent import UserAgent
import random

# Генерируем случайный user-agent

random_user_agent = UserAgent().random

class ScreenshotManager:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def capture_screenshot(self, url, full_page=True, output_path="screenshot.png"):
        """Захват скриншота всей страницы или видимой области"""
        self.driver.get(url)
        time.sleep(15)  # Ожидание загрузки контента
        
        if full_page:
            # Скриншот всей страницы

            total_height = self.driver.execute_script("return document.body.scrollHeight")
            time.sleep(3)
            total_widtht = self.driver.execute_script("return document.body.scrollWidth")
            self.driver.set_window_size(total_widtht, total_height)
            self.driver.save_screenshot(output_path)

        else:
            # Скриншот видимой области
            self.driver.save_screenshot(output_path)
        
        return output_path
    
    def find_ad_elements(self):
        """Поиск рекламных элементов по классу banner"""
        ad_elements = []
        banners = self.driver.find_elements(By.CSS_SELECTOR, 'div.banner')
        
        for banner in banners:
            try:
                location = banner.location
                size = banner.size
                if location and size:
                    ad_elements.append({
                        'x': location['x'],
                        'y': location['y'],
                        'width': size['width'],
                        'height': size['height']
                    })
            except Exception:
                continue
        
        return ad_elements
    
    def annotate_screenshot(self, screenshot_path, ad_elements, output_path="annotated_screenshot.png"):
        """Аннотирование скриншота с выделением рекламных областей"""
        with Image.open(screenshot_path) as img:
            draw = ImageDraw.Draw(img)
            
            for ad in ad_elements:
                # Рисуем красную рамку вокруг рекламного блока
                draw.rectangle(
                    [ad['x'], ad['y'], ad['x'] + ad['width'], ad['y'] + ad['height']],
                    outline="red",
                    width=3
                )
                
                # Добавляем текст "AD"
                draw.text(
                    (ad['x'] + 5, ad['y'] + 5),
                    f"AD, {ad['width']}, {ad['height']}",
                    fill="red"
                )
            
            img.save(output_path)
        return output_path
    
    def capture_and_annotate(self, url, full_page=True, output_path="result.png"):
        """Полный процесс захвата и аннотирования"""
        screenshot_path = self.capture_screenshot(url, full_page)
        ad_elements = self.find_ad_elements()
        return self.annotate_screenshot(screenshot_path, ad_elements, output_path)
    
    def close(self):
        """Закрытие драйвера"""
        self.driver.quit()


    def run_screen(self):
        manager = ScreenshotManager()
        try:
            result = manager.capture_and_annotate(
                url="https://ria.ru/",
                full_page=True,
                output_path="annotated_screenshot.png"
            )
            print(f"Скриншот сохранен: {result}")
            
        finally:
            manager.close()