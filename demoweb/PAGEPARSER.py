import time
import os
from PIL import Image, ImageDraw
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from LOGI import logger
from CONFIG import AdParserConfig
from fake_useragent import UserAgent


class PageParser:
    def __init__(self, config):
        self.config = config or AdParserConfig
        self.driver = None
        self.setup_driver()

        self.AD_SELECTORS = [
                "//div[contains(@class, 'yandex_rtb_')]",
                "//div[contains(@id, 'yandex_rtb_')]",
                "//div[contains(@id, 'adfox_')]",
                "//div[contains(@id, 'begun_block_')]"
            ]

    def setup_driver(self):
        """Настройка WebDriver"""
        try:
            chrome_options = Options()
            
            if self.config.HEADLESS:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument(f"--window-size={self.config.WINDOW_SIZE[0]},{self.config.WINDOW_SIZE[1]}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--user-agent={UserAgent().random}")
            
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

    def load_page(self, url) -> bool:
        try:
            logger.info(f"Загрузка страницы: {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            logger.info(f"Страница успешно загружена: {url}")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки страницы {url}: {e}")
            return False

    def elements(self):
        filter_elements = []
        seen = set()
        try:
            for selector in self.AD_SELECTORS:

                elements = self.driver.find_elements("xpath", selector)
                
                for element in elements:
                    if element.id not in seen and element.is_displayed():
                        seen.add(element.id)
                        filter_elements.append(element)

        except Exception as e:
            logger.error(f"Ошибка при обнаружении элемента: {e}")

        return filter_elements

    def detect_ads(self, elements):
        result = []
        for element in elements:
            try:
                data = [{
                    'element': element.id,
                    'tag': element.tag_name,
                    'classes': element.get_attribute('class'),
                    'id': element.get_attribute('id'),
                    'location': element.location,
                    'size': element.size,
                    'is_displayed': element.is_displayed()
                    }]
                
                result.append(data)

            except Exception as e:
                logger.error(f"Не удолось извлеч данные с элемента {e}")

        return result

    def screenshots_elements(self, screenshots_dir, elements):
        try:
            logger.info("Создание скриншотов реклам")

            try:
                overlaying_element = self.driver.find_element(By.CSS_SELECTOR, "div.widgets__b-slide")
                self.driver.execute_script("arguments[0].style.visibility='hidden'", overlaying_element)
            except NoSuchElementException:
                logger.info("Нижний виджет отсутствует")

            
            for element in elements:
                element.screenshot(f"{screenshots_dir}/screenshot{element.id}.png")
                time.sleep(2)
        except Exception as e:
            logger.error(f"Ошибка при создании скриншота элемента: {e}")

    def capture_screenshot_full_page(self, screenshots_dir):
        """Захват скриншота всей страницы"""
        output_path = f"{screenshots_dir}/full_screenshot{self.driver.name}.png"
        try:
            logger.info("Создание скриншота всей страницы")
            self.driver.execute_script("window.scrollTo(0, 0);")
            total_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            self.driver.set_window_size(self.config.WINDOW_SIZE[0], total_height+100)
            self.driver.save_screenshot(output_path)
            self.driver.set_window_size(self.config.WINDOW_SIZE[0],self.config.WINDOW_SIZE[1])
        except Exception as e:
            logger.error(f"Ошибка при захвате скриншота всей страницы: {e}")
        return output_path

    def annotate_screenshot_full_page(self, capture_screenshot_full_page, screenshots_dir, elements):
        """Aннотирование скриншота всей страницы"""
        try:
            logger.info("Aннотирование скриншота всей страницы")
            with Image.open(capture_screenshot_full_page) as amg:
                draw = ImageDraw.Draw(amg)

                for element in elements:
                    draw.rectangle([
                        element.location['x'],
                        element.location['y'],
                        element.location['x'] + element.size['width'],
                        element.location['y'] + element.size['height']
                        ], outline="red", width=3
                    )
                    draw.text(
                        (element.location['x'] + 5, element.location['y'] + 5),
                        f"AD, {element.size['width']}, {element.size['height']}",
                        fill="red"
                    )
                
                amg.save(f"{screenshots_dir}/annotated_full_screenshot.png")

        except Exception as e:
            logger.error(f"Ошибка при аннотировании скриншота всей страницы: {e}")

    def screenshots(self, elements):
        """Запуск для скриншота всей страницы и аннотирования ее"""
        script_path = os.path.abspath(__file__)
        dirname = os.path.dirname(script_path)
        screenshots_dir = os.path.join(dirname, "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        #self.screenshots_elements(screenshots_dir, elements)
        screenshot_path = self.capture_screenshot_full_page(screenshots_dir)
        self.annotate_screenshot_full_page(screenshot_path, screenshots_dir, elements)

    def click_elements(self, elements):
        logger.info("Начинаем клики по рекламным элементам")
        main_window = self.driver.current_window_handle
        ads_click = []
        try:
            overlaying_element = self.driver.find_element(By.CSS_SELECTOR, "div.widgets__b-slide")
            self.driver.execute_script("arguments[0].style.visibility='hidden'", overlaying_element)
        except NoSuchElementException:
            pass

        for i, element in enumerate(elements, start=1):
            try:
                time.sleep(3)
                ActionChains(self.driver).move_to_element_with_offset(element, -20, -10).click().perform()
                logger.info(f"Клик по {i} элементу")
                WebDriverWait(self.driver, 15).until(EC.number_of_windows_to_be(2))
                
                new_window = [window for window in self.driver.window_handles if window != main_window][0]

                self.driver.switch_to.window(new_window)

                current_url = self.driver.current_url

                utm_data = self.extract_utm_params(current_url)

                ad_data = [{
                    "id": element.id,
                    "current_url": current_url,
                    "title": self.driver.title,
                    "utm_params": utm_data
                }]

                self.driver.close()
                self.driver.switch_to.window(main_window)
            except Exception as e:
                logger.error(f"Не удолось кликнуть по {i} элементу: {e}")
                continue

            ads_click.extend(ad_data)

        return ads_click
    
    def extract_utm_params(self, url):
        """Извлекает UTM-метки из URL"""
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            utm_params = {}
            for key, value in query_params.items():
                if key.startswith('utm_'):
                    utm_params[key] = value[0]
        except Exception as e:
            logger.error(f"Ошибка при извлечении UTM-метки: {e}")
        return utm_params

    def close(self):
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver закрыт")
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
