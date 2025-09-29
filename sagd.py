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

def get_new_driver():
    random_version = randint(120, 140)
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--log-level=3")
    opts.add_argument("--remote-debugging-port=0")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_argument(
        f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) Chrome/{random_version}.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(20)
    return driver

def process_batch(args):
    links, batch_index = args
    column = ['Name', 'Type', 'min_power', 'max_power', 'min_frequency', 'max_frequency', 'Link']
    data = []
    driver = None

    try:
        driver = get_new_driver()
        for link in links:
            name = type_ = min_power_raw = max_power_raw = min_frequency_raw = max_frequency_raw = None
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

                try:
                    name = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/h1').text.strip()
                except:
                    pass
                try:
                    type_ = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[1]/table/tbody/tr[1]/td').text.strip()
                except:
                    pass
                try:
                    min_power_raw = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[2]/table/tbody/tr[1]/td').text
                except:
                    pass
                try:
                    max_power_raw = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[2]/table/tbody/tr[2]/td').text
                except:
                    pass
                try:
                    min_frequency_raw = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[3]/table/tbody/tr[1]/td').text
                except:
                    pass
                try:
                    max_frequency_raw = driver.find_element(By.XPATH, '//*[@id="product-data"]/div[1]/section/div[1]/div[1]/div[3]/table/tbody/tr[2]/td').text
                except:
                    pass

                min_power = keep_watts(min_power_raw)
                max_power = keep_watts(max_power_raw)
                min_frequency = keep_hertz(min_frequency_raw)
                max_frequency = keep_hertz(max_frequency_raw)

                data.append([
                    name or "None",
                    type_ or "None",
                    min_power or "None",
                    max_power or "None",
                    min_frequency or "None",
                    max_frequency or "None",
                    link
                ])
                print(f"[{batch_index}] {name or 'None'}")

            except Exception as e:
                print(f"[{batch_index}] Ошибка на {link}: {e}")

    finally:
        if driver:
            driver.quit()

    df = pd.DataFrame(data, columns=column)
    df.to_csv(f"parsed_batch_{batch_index}.csv", index=False, encoding="utf-8-sig")

def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

if __name__ == "__main__":
    start_time = time.time()

    final_links = pd.read_csv("links.csv")["url"].dropna().tolist()
    num_processes = 12
    batches = split_list(final_links, num_processes)

    with Pool(processes=num_processes) as pool:
        pool.map(process_batch, [(batch, i) for i, batch in enumerate(batches)])

    all_parts = [f for f in os.listdir() if f.startswith("parsed_batch_") and f.endswith(".csv")]
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
