
from selenium import webdriver


def get_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome('./chrome/chromedriver', options=options)
    driver.set_page_load_timeout(5)
    driver.set_script_timeout(5)
    return driver


def get_new_webdriver(driver):
    if driver:
        try:
            driver.close()
            driver.quit()
        except:
            pass
    return get_webdriver()


def close_driver(driver):
    try:
        driver.quit()
        driver.close()
    except:
        pass


