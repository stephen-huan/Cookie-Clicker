import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from termcolor import colored, cprint

#TODO: Upgrades, better number parsing
#Golden cookie: class "shimmer"
#Golen cookie - can't multithread; main time crunch clicker funtion - add cookie detection after n iterations?

class Buyable:
    """ An object that can be purchased. The main goal of cookie clicker is to pick the optimal one each iteration """

    def __init__(self):
        self.name = ""
        self.cookies = self.number = self.index = self.upgrade = 0
        self.cps = 0.0

    def __str__(self):
        return "Name: {}; Cookies: {}; CPS: {}; Heuristic: {}".format(self.name, self.cookies, str(self.cps)[:str(self.cps).index(".") + 3], h(self))

#SELENIUM HELPER METHODS
def find(id, mode=By.ID, parent=None, delay=10):
    """ Waits for a WebElement to be clickable, returns that element """
    if not parent: parent = driver
    return WebDriverWait(parent, delay).until(EC.element_to_be_clickable((mode, id)))

def click(id, mode=By.ID, parent=None):
    if not parent: parent = driver
    stale = True
    while stale:
        try:
            find(id, mode).click()
            stale = False
        except (StaleElementReferenceException, WebDriverException):
            print("Element stale! Trying again to click")

def make_driver(x, y):
    """ Makes a new WebDriver with a certain size """
    chrome_options = Options()
    chrome_options.add_argument("--window-size={},{}".format(x, y))
    return webdriver.Chrome(chrome_options=chrome_options)

#COOKIE CLICKER INTERACTIONS
def load():
    while len(driver.find_elements_by_id("loader")) > 0:
        if len(driver.find_elements_by_id("failedToLoad")) > 0:
            driver.refresh()
            print("Refreshed")

def rename(name):
    """ Renames your bakery """
    click("bakeryName")
    find("bakeryNameInput").send_keys(name)
    click("promptOption0")

def close_notifs():
    """ Closes open notifications """
    while len(driver.find_elements_by_css_selector("div.framed.note.haspic.hasdesc")) > 0:
        click("close", By.CLASS_NAME, find("div.framed.note.haspic.hasdesc", By.CSS_SELECTOR))

def cookie_clicker(choice):
    """ Clickes the cookie until a certain value"""
    i = 0
    estimated = t(choice)*rate
    start = time.time()
    while i < estimated or cookies() < choice.cookies:
        i += 1
        cookie.click()

def measure_cps(length=10): #about 22 cps
    """ Measures the CPS. Should be done on a clean run (no buildings) """
    count = cookies()
    start = time.time()
    while time.time() - start < length:
        cookie.click()
    return (cookies() - count)/length

#MAIN METHODS
def display():
    """ Displays information to the user """
    cprint("Current cookies in bank: " + str(cookies()), 'blue', end='\n')
    cprint("Current cookies per second (CPS): {}".format(round(current_cps, 2)), 'green', end='\n')
    cprint("Guesstimated rate: {}; Cookies/click: {}; CPS from mouse: {}".format(round(rate, 2), cookies_a_click, round(rate*cookies_a_click, 2)), 'green', end='\n')
    for buyable in buyables: print(buyable)
    cprint("Choice: " + choice.name, 'red', end='\n')

def parse(str, dtype=int):
    """ Parses the unique format of cookie clicker numbers """
    str = str.replace(",", "")
    if len(str.split()) > 1:
        words = {"million" : 10**6}
        for word in words:
            if word in str.split()[1]:
                return words[word]*dtype(str.split()[0])
    return dtype(str)

def get_tooltips():
    """ Mouses over each tooltip and reads the information """
    #products, upgrades
    rtn = ([], [])
    lengths = (len(driver.find_elements_by_css_selector("div.product.unlocked")) + 1, len(find("upgrades").find_elements_by_css_selector("div")))
    for j, name in enumerate(["product", "upgrade"]):
        for i in range(lengths[j]):
            ActionChains(driver).move_to_element(find(name + str(i))).perform()
            rtn[j].append(driver.find_element_by_id("tooltip").text)
    return rtn

def get_buyables():
    tooltips = get_tooltips()
    products, upgrades = [], []
    for j in range(2):
        for i, tooltip in enumerate(tooltips[j]):
            buyable = Buyable()
            buyable.index = i
            tooltip = tooltip.split("\n")
            if len(tooltip) >= 3 and tooltip[1] != "[Achievement] [Locked]":
                buyable.cookies = parse(tooltip.pop(0))
                buyable.name = tooltip.pop(0)
                if j == 0:
                    buyable.number = parse(tooltip[0].split()[-1][:-1])
                    try:
                        buyable.cps = parse(tooltip[2].split()[4], float) if len(tooltip) > 2 else parse(str(7*products[-1].cps), float)
                    except IndexError:
                        buyable.cps = 0.1
                    products.append(buyable)
                else:
                    buyable.upgrade = 1
                    value = 0
                    words = [x.name.lower() for x in products] + ["mouse"]
                    numwords = {"twice" : 1}
                    descr = tooltip[1].lower()
                    num = 0
                    for key in numwords:
                        if key in descr:
                            num = numwords[key]
                    if "mouse" in buyable.name:
                        buyable.cps = 0.01*current_cps*rate
                    if "fingers" in buyable.name:
                        num = 0.1*sum(x.number for x in products)/cookies_a_click
                    if "cookie" in buyable.name:
                        buyable.cps = 0.01*sum(x.cps for x in product)
                    for word in words:
                        if word in descr:
                            if word == "mouse":
                                buyable.cps += num*rate*cookies_a_click
                            else:
                                for x in buyables:
                                    if x.name == word[0].upper() + word[1:]:
                                        break
                                buyable.cps += num*x.cps*x.number
                    upgrades.append(buyable)
    return products + upgrades

#MATH
def t(x): return max((x.cookies - current_cookies)/(current_cps + rate*cookies_a_click), 0)
def v(x): return x.cps/x.cookies
def h(x): return v(x)/(t(x) + 1)

if __name__ == "__main__":
    print("Cookie Clicker Player 1.0.0\nMade by Stephen Huan")

    driver = make_driver(1920, 1080)
    driver.get("http://orteil.dashnet.org/cookieclicker/")
    load() #Doesn't actually do anything
    rename("Stephen")
    click("a.cc_btn.cc_btn_accept_all", By.CSS_SELECTOR)
    click("statsButton")
    cookie = find("bigCookie")
    rate = 20
    while True:
        buyables = get_buyables()
        current_cookies = parse(find("cookies").text.split("\n")[0].split()[0])
        current_cps = parse(find("cookies").text.split("\n")[1].split()[-1])
        cookies_a_click = parse(find("subsection", By.CLASS_NAME).find_elements_by_class_name("listing")[6].text.split()[-1], float)
        choice = max(buyables, key=lambda x: h(x))
        display()
        cookie_clicker(choice)
        click(("product" if choice.upgrade == 0 else "upgrade") + str(choice.index))
        close_notifs()
