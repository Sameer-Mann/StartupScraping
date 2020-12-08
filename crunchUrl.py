from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from json.decoder import JSONDecodeError
from json import load,dump
from time import sleep
from random import randrange

from startupList import read_file,parseCrunchPage

base_url = "https://www.crunchbase.com"
# def proxy():

#     prox = Proxy()
#     prox.proxy_type = ProxyType.MANUAL
#     prox.http_proxy = "ip_addr:port"
#     prox.socks_proxy = "ip_addr:port"
#     prox.ssl_proxy = "ip_addr:port"

#     capabilities = webdriver.DesiredCapabilities.CHROME
#     prox.add_to_capabilities(capabilities)
#     return capabilities

def getNamesAndLinks():
    data = read_file()
    return [*data.keys()],[*data.values()]

def write(data,file_name):
    with open(f"{file_name}.json","w") as f:
        dump(data,f)

def getDrivers():
    driver = webdriver.Chrome()
    return [driver]

def search(driver,name):
    try:
        ip = driver.find_element_by_tag_name("input")
        ip.click()
        driver.execute_script("document.querySelector('input').value = ''")
        ip.send_keys(name)
        searchArea = WebDriverWait(driver,4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                "search-results-section[class='ng-star-inserted']")
            ))
        WebDriverWait(driver,4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                "search-results-section[class='ng-star-inserted']>mat-card>div>button")
            )).click()
    except (TimeoutException,NoSuchElementException):
        pass

def getUrlObjects(driver,discovered):
    """also adds the current urls to data"""
    names = []
    anchor_tags = []
    try:
        anchor_tags = driver.find_elements_by_css_selector(
            'search-results-section[class="ng-star-inserted"]>mat-card>a')
        for tag in anchor_tags:
            url = tag.get_property("href")
            name = tag.find_element_by_css_selector('span>span').text
            names.append(name)
            discovered[name] = url
    except NoSuchElementException:
        pass
    return names,anchor_tags

def parseLink(names,anchor_tags,driver,final_data):
    idx = randrange(0,len(anchor_tags))
    anchor_tags[idx].click()
    data = parseCrunchPage(driver)
    final_data[names[idx]] = data


def loadData(name):
    data = {}
    try:
        data = load(open(f"{name}.json","r"))
    except JSONDecodeError as e:
        pass
    return data

def crunch():
    # driver = webdriver.Chrome(desired_capabilities=proxy())
    drivers = getDrivers()
    driver = drivers[0]
    driver.get(base_url)
    names,links = getNamesAndLinks()

    final_data = loadData("data")
    searched = loadData("searched")
    discovered = loadData("discovered")
    
    values,anchor_tags = [],[]

    for _,name in enumerate(names):
        if name in searched:
            continue
        try:
            chosen = randrange(1,3)
            x = randrange(6,12)
            print(f"Sleeping {x}s")
            sleep(x)

            if chosen == 1:
                search(driver,name)
                values,anchor_tags = getUrlObjects(driver,discovered)
                searched[name]=True
            elif len(values):
                parseLink(values,anchor_tags,driver,final_data)
                values = []
        except:
            break

    write(final_data,"data")
    write(searched,"searched")
    write(discovered,"discovered")

if __name__ == '__main__':
    crunch()