import os
import time
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def handle_ad_interaction():
    options_chrome = Options()
    #options_chrome.add_argument("--headless")
    options_chrome.add_argument("--no-sandbox")
    #options_chrome.add_argument("--window-size=1920,1080")
    options_chrome.add_argument(f"--user-agent={UserAgent().random}")
    options_chrome.add_argument('--disable-blink-features=AutomationControlled')
    options_chrome.add_argument("--start-maximized")
    options_chrome.add_argument("--disable-dev-shm-usage")
    options_chrome.add_argument("--disable-gpu")
    options_chrome.add_argument("--disable-extensions")
    options_chrome.add_argument("--disable-notifications")
    options_chrome.add_argument("--disable-popup-blocking")
    options_chrome.add_argument("--disable-infobars")
    options_chrome.add_argument("--disable-blink-features=AutomationControlled")
    options_chrome.add_experimental_option("excludeSwitches", ["enable-automation"])
    options_chrome.add_experimental_option('useAutomationExtension', False)


    driver = webdriver.Chrome(options=options_chrome)
    driver.get("https://ria.ru/")
    time.sleep(3)

    # Сохраняем идентификатор текущего окна
    main_window = driver.current_window_handle
    print(main_window)
    time.sleep(3)
    screenshot_folder = "screenshots"
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    
    try:
        # Ожидаем появления рекламного блока
        banners = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.banner__co ntent"))
        )
        time.sleep(3)
        for banner in banners:
            try:
                if banner.size['height'] and banner.size['width'] != 0:
                    print(f"Высота рекламного боннера: {banner.size['height']}")
                    print(f"Ширина рекламного баннера: {banner.size['width']}")

                    ActionChains(driver).scroll_to_element(banner)
                    ActionChains(driver).perform
                    #driver.execute_script("arguments[0].scrollIntoView();", banner)

                    #banner.click()
                    #ActionChains(driver).move_to_element(banner).click().perform()
                    x_offset = 50
                    y_offset = 0
                    ActionChains(driver).move_to_element_with_offset(banner, x_offset, y_offset).click().perform()

                    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

                    new_window = [window for window in driver.window_handles if window != main_window][0]
                    driver.switch_to.window(new_window)

                    driver.save_screenshot(os.path.join(screenshot_folder, f"{driver.current_window_handle}.png"))

                    redirect_info = {
                        'current_url': driver.current_url,
                        'title': driver.title,
                        'id': driver.current_window_handle
                    }
                    print(redirect_info)
                    driver.close()
                    time.sleep(3)
                    driver.switch_to.window(main_window)
                
            except Exception as e:
                print(f"Ошибка с элементом : {e}")
                continue






        #time.sleep(3)
        # Кликаем по баннеру
        #banner.click()
        #time.sleep(3)
        # Ожидаем перехода и обрабатываем новое окно/вкладку
        #WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        
        # Переключаемся на новую вкладку
        #new_window = [window for window in driver.window_handles if window != main_window][0]
        #driver.switch_to.window(new_window)

        #driver.save_screenshot("visible_viewport.png")

        # Получаем информацию о переходе
        #redirect_info = {
        #    'current_url': driver.current_url,
        #    'title': driver.title
        #}
        
        # Закрываем рекламную вкладку и возвращаемся
        #driver.close()

        #driver.switch_to.window(main_window)

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        
    finally:
        driver.quit()

# Пример использования
if __name__ == "__main__":

    handle_ad_interaction()
