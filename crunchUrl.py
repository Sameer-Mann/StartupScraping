from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException,WebDriverException
from traceback import print_stack

from json.decoder import JSONDecodeError
from json import load,dump
from time import sleep
from random import randrange
from startupList import read_file,parseCrunchPage,FindAllByCss,FindOneByCss

base_url = "https://www.crunchbase.com"

def getNamesAndLinks():
    data = read_file()
    return [*data.keys()],[*data.values()]

def write(data,file_name):
    with open(f"{file_name}.json","w") as f:
        dump(data,f)

def getDrivers():
    driver1 = webdriver.Chrome()
    driver1.get(base_url)
    driver1.maximize_window()
    driver = webdriver.Firefox()
    driver.get(base_url)
    driver1.maximize_window()
    return [driver,driver1]

def search(driver,name):
    try:
        ip = FindOneByCss(driver,"input")
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
    try:
        anchor_tags = FindAllByCss(driver,
            'search-results-section[class="ng-star-inserted"]>mat-card>a')
        for tag in anchor_tags:
            url = tag.get_property("href")
            name = FindOneByCss(tag,"span>span").text
            names.append(name)
            discovered[name] = url
    except NoSuchElementException:
        pass
    return names

def parseLink(names,driver,final_data):
    anchor_tags = anchor_tags = FindAllByCss(driver,
            'search-results-section[class="ng-star-inserted"]>mat-card>a')
    if len(anchor_tags) == 0:
        return
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

def changeDriver(drivers,driver):
    if driver == drivers[0]:
        return drivers[1]
    return drivers[0]

def crunch():
    # driver = webdriver.Chrome(desired_capabilities=proxy())
    drivers = getDrivers()
    # driver = drivers[0]
    # driver.get(base_url)
    names,links = getNamesAndLinks()

    final_data = loadData("data")
    searched = loadData("searched")
    discovered = loadData("discovered")
    driver = drivers[0]

    for i,name in enumerate(names):
        if name in searched:
            print(f"Skipping {i}th")
            continue
        try:
            chosen = randrange(1,3)
            if chosen == 1:
                print(f"Searching {i}th")
                search(driver,name)
                values = getUrlObjects(driver,discovered)
                searched[name]=True
                chosen1 = randrange(1,3)
                if chosen1 == 1:
                    sleep(2.5)
                    print(f"Clicking Random")
                    parseLink(values,driver,final_data)
                driver = changeDriver(drivers,driver)
            elif name in discovered:
                driver.get(discovered[name])
                final_data[name] = parseCrunchPage(driver)
                driver = changeDriver(drivers,driver)
            else:
                continue
            x = randrange(4,9)
            print(f"Sleeping {x}s")
            sleep(x)
        except KeyboardInterrupt:
            break
        except WebDriverException as e:
            print_stack()
            print(e)
            break
        except Exception as e:
            print_stack()
            print(e)
            break

    write(final_data,"data")
    write(searched,"searched")
    write(discovered,"discovered")
    drivers[0].quit()
    drivers[1].quit()
if __name__ == '__main__':
    crunch()