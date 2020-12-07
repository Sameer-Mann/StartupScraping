import requests
from lxml import html
from selenium import webdriver

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

def parseCrunchPage(driver,url):
    """
    driver will be webdriver object from selenium
    data will contain these keys
    "headquarters","industries","founder","founded_in",
    "funding","team_size","contact_email",
    "contact_phone","description"
    fackebook_link,twitter_link,linkendin_link
    """
    driver.get(url)
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
    arr = driver.find_elements_by_css_selector("fields-card>ul")

    data["headquarters"] = ','.join(map(lambda x:x.text,
        arr[0].find_elements_by_css_selector("span>a")))

    data["industries"] = ','.join(map(lambda x:x.text,
        arr[1].find_elements_by_css_selector("mat-chip")))

    for li in arr[4].find_elements_by_css_selector("li"):
        anchor_tag = li.find_element_by_css_selector("a")
        site = anchor_tag.get_property("title").split()[-1].lower().strip()
        data[f"{site}_link"] = anchor_tag.get_property("href")

    arr1 = arr[1].find_elements_by_css_selector('li') 
    arr1 += arr[3].find_elements_by_css_selector('li')
    arr1 += driver.find_elements_by_css_selector("anchored-values>a")
    for li in arr1:
        value = ""
        fName_list = [*map(lambda x:x.text.lower().strip(),li.find_elements_by_css_selector("span>span"))]
        name = fName_list[0]
        if name == "":
            name = fName_list[1]
        if name in ["industries","headquarters"] or name not in mapping:
            continue
        value = li.find_elements_by_css_selector(mapping[name]["selector"])
        val = ""
        if name == "founders":
            val = ",".join(map(lambda x:x.text, value))
        else:
            val = value[0].text
        data[mapping[name]["key"]] = val

    return data
