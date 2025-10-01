import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Pool
from random import randint

def keep_watts(text):
    return text.strip() if text and "Вт" in text else None

def keep_hertz(text):
    return text.strip() if text and "Гц" in text else None

def get_new_driver(request_counter):
    if request_counter % 10 == 0:
        random_version = randint(120, 140)
    else:
        random_version = 120

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--log-level=3")
    opts.add_argument("--remote-debugging-port=0")  
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random_version}.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(20)
    return driver


def process_single(args):
    link, index = args
    column = ['Name', 'Type', 'min_power', 'max_power', 'min_frequency', 'max_frequency', 'Link']
    name = type_ = min_power_raw = max_power_raw = min_frequency_raw = max_frequency_raw = None

    try:
        driver = get_new_driver(index)
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        try:
            name = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/h1').get_attribute('textContent').strip()
        except:
            pass
        try:
            type_ = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[1]/table/tbody/tr[1]/td').get_attribute('textContent').strip()
        except:
            pass
        try:
            min_power_raw = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[2]/table/tbody/tr[1]/td').get_attribute('textContent')
        except:
            pass
        try:
            max_power_raw = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[2]/table/tbody/tr[2]/td').get_attribute('textContent')
        except:
            pass
        try:
            min_frequency_raw = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[3]/table/tbody/tr[1]/td').get_attribute('textContent')
        except:
            pass
        try:
            max_frequency_raw = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[3]/table/tbody/tr[2]/td').get_attribute('textContent')
        except:
            pass

    except Exception as e:
        print(f"Ошибка на {link}: {e}")

    finally:
        if 'driver' in locals():
            driver.quit()

        min_power = keep_watts(min_power_raw)
        max_power = keep_watts(max_power_raw)
        min_frequency = keep_hertz(min_frequency_raw)
        max_frequency = keep_hertz(max_frequency_raw)

        row = [[
            name if name else None,
            type_ if type_ else None,
            min_power if min_power else None,
            max_power if max_power else None,
            min_frequency if min_frequency else None,
            max_frequency if max_frequency else None,
            link
        ]]

        df = pd.DataFrame(row, columns=column)
        df = df.replace(r'^\s*$', None, regex=True)
        df = df.where(pd.notnull(df), "None")
        df.to_csv(f"parsed_single_{index}.csv", index=False, encoding="utf-8-sig")
        print(f"[{index}] {name if name else 'None'}")

if __name__ == "__main__":
    start_time = time.time()

    final_links = pd.read_csv("links.csv")["url"].dropna().tolist()

    with Pool(processes=10) as pool:
        pool.map(process_single, [(link, i) for i, link in enumerate(final_links)])

    all_parts = [f for f in os.listdir() if f.startswith("parsed_single_") and f.endswith(".csv")]
    dfs = [pd.read_csv(f) for f in sorted(all_parts)]
    final_df = pd.concat(dfs, ignore_index=True)
    final_df = final_df.replace(r'^\s*$', None, regex=True)
    final_df = final_df.where(pd.notnull(final_df), "None")
    final_df.to_csv("parsed_data.csv", index=False, encoding="utf-8-sig")
    
    for f in all_parts:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Не удалось удалить {f}: {e}")

    elapsed_time = time.time() - start_time
    print("Данные сохранены в parsed_data.csv")
    print(f"Время выполнения: {elapsed_time:.2f} секунд")
