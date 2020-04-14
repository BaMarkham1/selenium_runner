from selenium import webdriver
import os
import pandas as pd

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
driver.get("https://www.pro-football-reference.com/years/2019/rushing_advanced.htm")
tables = pd.read_html(browser.page_source)
print("num of tables:", str(len(tables)))
for index, table in enumerate(tables):
    print("Index:", str(index))
    for col in list(table.columns):
        print(col)
