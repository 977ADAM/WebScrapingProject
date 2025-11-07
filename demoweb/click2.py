import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def handle_ad_interaction():
    driver = webdriver.Chrome()
    driver.get("https://ria.ru/")
    time.sleep(10)
    original_window = driver.current_window_handle
    print(original_window)
    
    try:
        # Поиск рекламных блоков с ожиданием загрузки
        banners = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.banner__content"))
        )
        
        if not banners:
            print("Рекламные блоки не найдены")
            return

        # Клик по первому найденному баннеру
        banners[0].click()
        print("Успешный клик по рекламному блоку")

        # Ожидание перехода и сбор информации
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        # Переключение на новую вкладку
        new_window = [window for window in driver.window_handles if window != original_window][0]
        driver.switch_to.window(new_window)
        
        # Сбор данных о переходе
        ad_data = {
            "current_url": driver.current_url,
            "title": driver.title,
            "window_handle": new_window
        }
        print(f"Данные перехода: {ad_data}")

        # Закрытие вкладки и возврат
        driver.close()
        driver.switch_to.window(original_window)
        print("Успешное возвращение на исходную страницу")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    handle_ad_interaction()