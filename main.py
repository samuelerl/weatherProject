from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.keys import Keys
import json
import requests
import re

ZIP1="94538"
ZIP2="94103"
ZIP3="90012"

URL1="https://www.accuweather.com/en/us/fremont/" + ZIP1 + "/daily-weather-forecast/332130"
URL2="https://www.accuweather.com/en/us/san-francisco/"+ ZIP2 + "/daily-weather-forecast/347629"
URL3="https://www.accuweather.com/en/us/los-angeles/" +ZIP3 + "/daily-weather-forecast/347625"

APIKEY = "YCOzRwbARFzvym7iQtSFiamGpgQYGtQQ"

driver = webdriver.Chrome("/usr/local/bin/chromedriver")
driver.implicitly_wait(10)

timeout = 60
wait = WebDriverWait(driver, timeout)

#Find cities and their forecasts
forecast = {}
forecastAPI = {}

def getForecast(url):
    result=[]
    driver.get(url)
    for i in range(3):
        high = driver.find_element_by_xpath("//div[@data-qa='dailyCard"+str(i)+"']//span[@class='high']").text
        low = driver.find_element_by_xpath("//div[@data-qa='dailyCard"+str(i)+"']//span[@class='low']").text
        result.append({"high":int(re.findall(r'\d+', high)[0]), "low":int(re.findall(r'\d+', low)[0])})
    return(result)

def getForecastAPI(zip):
    result = []
    resp = requests.get(
        "http://dataservice.accuweather.com/locations/v1/postalcodes/search?q="+zip+"'&apikey=" + APIKEY)
    key = resp.json()[0]["Key"]

    resp = requests.get(
        "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + key + "?apikey=" + APIKEY)
    for i in range(3):
        low = resp.json()["DailyForecasts"][i]["Temperature"]["Minimum"]["Value"]
        high = resp.json()["DailyForecasts"][i]["Temperature"]["Maximum"]["Value"]
        result.append({"high":int(high), "low":int(low)})
    return (result)
#str to int, float to int
forecast = {ZIP1:getForecast(URL1)}, {ZIP2:getForecast(URL2)}, {ZIP3:getForecast(URL3)}
forecastAPI = {ZIP1:getForecastAPI(ZIP1)}, {ZIP2:getForecastAPI(ZIP2)}, {ZIP3:getForecastAPI(ZIP3)}
assert (forecast==forecastAPI)
time.sleep(5)
#driver.close()




