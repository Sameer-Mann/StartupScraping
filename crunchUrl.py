from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException,WebDriverException

from selenium.webdriver.common.proxy import Proxy, ProxyType
from traceback import print_stack

from json.decoder import JSONDecodeError
from json import load,dump
from time import sleep
from random import randrange
from startupList import read_file,parseCrunchPage,FindAllByCss,FindOneByCss
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib3.exceptions import HTTPError
from random import shuffle
# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy

base_url = "https://www.crunchbase.com"

def getNamesAndLinks():
    data = read_file()
    return set([*data.keys()]),set([*data.values()])

def write(data,file_name):
    with open(f"{file_name}.json","w") as f:
        dump(data,f)

def getDrivers():
    co1 = webdriver.ChromeOptions()
    co1.add_argument("--headless")

    co2 = webdriver.FirefoxOptions()
    co2.add_argument("--headless")

    drivers = [webdriver.Firefox(options=co2),webdriver.Safari()]
    # co.add_argument("log-level=3")
    for driver in drivers:
        driver.maximize_window()
    return drivers

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
    idx = drivers.index(driver)
    return drivers[(idx+1)%len(drivers)]

def crunch():
    drivers = getDrivers()
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

def indiaData():
    drivers = getDrivers()
    names,links = getNamesAndLinks()
    final_data = loadData("data")
    india_data = loadData("india")
    discovered = loadData("discovered")
    driver = drivers[0]
    urls = []
    names1 = [*discovered.keys()]
    shuffle(names1)
    names1 = names1[:90]
    for _,name in enumerate(names1):
        if name in final_data:
            continue
        try:
            urls.append(base_url+f"/organization/{discovered[name]}")
            if len(urls) == 2:
                with ThreadPoolExecutor() as exc:
                    results = [exc.submit(parseCrunchPage,drivers[i],urls[i]) for i in range(2)]
                    for i,res in enumerate(as_completed(results)):
                        data = res.result()
                        if len(data) == 0:
                            print(f"Failed {urls[i]}")
                            continue
                        print(f"Succes {urls[i]}")
                        if "headquarters" in data and data["headquarters"].split(",")[-1] == "India":
                            india_data[name] = data
                        else:
                            final_data[name] = data
                urls = []
                x=randrange(5,8)
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
        except:
            break

    write(india_data,"india")
    write(final_data,"data")

    for driver in drivers:
        driver.quit()

if __name__ == '__main__':
    indiaData()