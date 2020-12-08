import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException

def write_file(names,links):
    """writes data to csv in form name,url
    excpets names and links as array of strings
    """
    with open("names.csv","w") as f:
        f.write("name,url\n")
        for i in range(len(links)):
            f.write(f"{names[i]},{links[i]}\n")

def getFromStartupList():
    """Gets name and url of all new-delhi startups on
    https://startups-list.com/
    """
    data = requests.get("https://new-delhi.startups-list.com/")
    tree = html.fromstring(data.content)
    links = [elem.get("href") for elem in tree.cssselect("#wrap>div>a")]
    names = [elem.text.strip() for elem in tree.cssselect("#wrap>div>a>h1") ]
    write_file(names,links)

def read_file():
    """Reads names.csv and return a dictionary
    with name:url (key:value)
    """
    d = {}
    with open("names.csv","r") as f:
        data = f.read().split("\n")
        for line in data[1:]:
            if line == "":
                continue
            name,url = line.split(",")
            d[name]=url
    return d

def checkIfSiteExists(url,timeout):
    fl=False
    try:
        fl = requests.get(url,timeout=timeout).status_code == 200
    except:
        # sometimes the connection takes too long
        pass
    return fl

def FindOneByCss(driver,selector):
    element = ""
    try:
        element = driver.find_element_by_css_selector(selector)
    except NoSuchElementException:
        pass
    return element

def FindAllByCss(driver,selector):
    elements = ""
    try:
        elements = driver.find_elements_by_css_selector(selector)
    except NoSuchElementException:
        pass
    return elements

def parseCrunchPage(driver):
    """
    driver will be webdriver object from selenium
    data will contain these keys
    "headquarters","industries","founder","founded_in",
    "funding","team_size","contact_email",
    "contact_phone","description","url"
    fackebook_link,twitter_link,linkendin_link
    https://www.crunchbase.com/organization/trilongo
    https://www.crunchbase.com/organization/wish
    """
    data = {}
    mapping = {
        "founded":{
            "selector":"field-formatter>span",
            "key":"founded_in"
        },
        "founders":{
            "selector":"span>a",
            "key":"founder"
        },
        "contact":{
            "selector":"blob-formatter>span",
            "key":"contact_email"
        },
        "phone":{
            "selector":"blob-formatter>span",
            "key":"contact_phone"
        },
        "total funding":{
            "selector":"field-formatter>span",
            "key":"funding"
        },
        "number of current team":{
            "selector":"field-formatter>span",
            "key":"team_size"
        }
    }
    def setSingle(key,driver,selector,prop="",text=False):
        value = FindOneByCss(driver,selector)
        if value:
            if prop:
                value = value.get_property(prop)
            elif text:
                value = value.text
            data[key] = value
    def setSingle1(key,driver,selector,func=None):
        values = FindAllByCss(driver,selector)
        if values:
            if func:
                values = [*map(func,values)]
            data[key] = ",".join(values)

    try:
        arr = WebDriverWait(driver,4).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"fields-card>ul")))
    except TimeoutException:
        arr = []

    if len(arr) == 0:
        return data

    setSingle("url",arr[0],"link-formatter>a",prop="href")
    setSingle("description",driver,"description-card>div>span",text=True)
    setSingle1("headquarters",arr[0],"span>a",func=lambda x:x.text.strip())
    if len(arr) >= 2:
        setSingle1("industries",arr[1],"mat-chip",func=lambda x:x.text.strip())

    anchor_tags = FindAllByCss(arr[-1],"link-formatter>a")
    if len(anchor_tags):
        for anchor_tag in anchor_tags:
            site = anchor_tag.get_property("title").split()[-1].lower().strip()
            data[f"{site}_link"] = anchor_tag.get_property("href")
    arr1 = FindAllByCss(arr[1],'li')
    if len(arr)>=4:
        arr1 += FindAllByCss(arr[3],'li')
    a = FindAllByCss(driver,"anchored-values>a")
    if a:
        arr1 += a
    for elem in arr1:
        fName_list = [*map(lambda x:x.text.lower().strip(),FindAllByCss(elem,"span>span"))]
        if len(fName_list) == 0:
            continue
        name = fName_list[0]
        if name == "" and len(fName_list)>=2:
            name = fName_list[1]
        if name in ["industries","headquarters"] or name not in mapping:
            continue
        value = FindAllByCss(elem,mapping[name]["selector"])
        val = ""
        if name == "founders":
            val = ",".join(map(lambda x:x.text, value))
        else:
            val = value[0].text
        data[mapping[name]["key"]] = val
    return data
