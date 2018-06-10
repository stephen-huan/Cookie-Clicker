import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from termcolor import colored, cprint

#TODO: Upgrades, better number parsing, cps function modification, better cookies/click calculation
#Golden cookie: class "shimmer"

class Buyable:

    def __init__(self, name, cookies, cps, index, upgrade):
        self.name = name
        self.cookies = cookies
        self.cps = cps
        self.index = index
        self.upgrade = upgrade

    def __str__(self):
        return "Name: {}; Cookies: {}; CPS: {}; Heuristic: {}".format(self.name, self.cookies, str(self.cps)[:str(self.cps).index(".") + 3], h(self.index, self.upgrade))


def find(id, mode=By.ID, parent=None, delay=10):
    """ Waits for a WebElement to be clickable, returns that element """
    if not parent: parent = driver
    for i in range(2):
        try: return WebDriverWait(parent, delay).until(EC.element_to_be_clickable((mode, id)))
        except: pass
    sys.exit("Didn't find element")

def make_driver(x, y):
    """ Makes a new WebDriver with a certain size """
    chrome_options = Options()
    chrome_options.add_argument("--window-size={},{}".format(x, y))
    return webdriver.Chrome(chrome_options=chrome_options)

def load():
    while len(driver.find_elements_by_id("loader")) > 0:
        if len(driver.find_elements_by_id("failedToLoad")) > 0:
            driver.refresh()
            print("Refreshed")

def rename(name):
    """ Renames your bakery """
    find("bakeryName").click()
    find("bakeryNameInput").send_keys(name)
    find("promptOption0").click()

def close_notifs():
    """ Closes open notifications """
    for i in range(len(driver.find_elements_by_css_selector("div.framed.note.haspic.hasdesc"))):
        find("close", By.CLASS_NAME, find("div.framed.note.haspic.hasdesc", By.CSS_SELECTOR)).click()
    # if len(driver.find_elements_by_css_selector("div.framed.close.sidenote")) > 0:
    #     find("div.framed.close.sidenote", By.CSS_SELECTOR).click()

def cookie_clicker(choice, mode):
    """ Clickes the cookie until a certain value"""
    i = 0
    estimated = t(choice, mode)*rate
    start = time.time()
    while i < estimated or cookies() < cookies(choice, mode):
        i += 1
        cookie.click()

def parse(str, dtype=int):
    """ Parses the unique format of cookie clicker numbers """
    return dtype(str.replace(",", ""))

def cookies(*arg, mode=0):
    """ No arg: Return the current number of cookies in the bank. Arg: returns cost """
    if len(arg) == 0:
        return parse(find("cookies").text.split("\n")[0].split()[0])
    return info[mode][0][arg[0]] if arg[0] < len(info[mode][0]) else parse(find("productPrice" + str(arg[0])).text)

def cps(*arg, mode=0):
    """ No arg: returns current cookies per second (CPS). Arg: returns net CPS gain """
    if len(arg) == 0:
        return parse(find("cookies").text.split("\n")[1].split()[-1], float)
    return info[mode][1][arg[0]] if arg[0] < len(info[mode][1]) else 7**(arg[0] - len(info[mode][1]) + 1)*info[mode][1][-1]

def get_num(x):
    """ Gets the number of buildings bought """
    return parse(find("productOwned" + str(x)).text)

def cookies_per_click():
    """ Finds the amount of cookies gained per click """
    return parse(find("subsection", By.CLASS_NAME).find_elements_by_class_name("listing")[6].text.split()[-1], float)

def measure_cps(length=10): #about 22 cps
    count = cookies()
    start = time.time()
    while time.time() - start < length:
        cookie.click()
    return (cookies() - count)/length

def get_tooltips(length, upgrade=False):
    rtn = []
    name = "upgrade" if upgrade else "product"
    for i in range(length):
        ActionChains(driver).move_to_element(find(name + str(i))).perform()
        rtn.append(find("tooltip").text)
    return rtn

def t(x, i=0): return max((cookies(x, i) - cookies())/(current_cps + rate*cookies_a_click), 0)
def v(x, i=0): return cps(x, i)/cookies(x, i)
def h(x, i=0): return v(x, i)/(t(x, i) + 1)

if __name__ == "__main__":
    print("Cookie Clicker Player 1.0.0\nMade by Stephen Huan")

    driver = make_driver(1920, 1080)
    driver.get("http://orteil.dashnet.org/cookieclicker/")
    load() #Doesn't actually do anything
    rename("Stephen")
    find("a.cc_btn.cc_btn_accept_all", By.CSS_SELECTOR).click()
    find("statsButton").click()
    cookie = find("bigCookie")
    rate = 20
    product_info = ([], [0.1], []) #price, cps, name
    while True:
        products, upgrades = len(driver.find_elements_by_css_selector("div.product.unlocked")), len(driver.find_elements_by_css_selector("div.crate.upgrade"))
        tooltips = (get_tooltips(products), get_tooltips(upgrades, True))
        upgrade_info = ([], [], [])
        info = (product_info, upgrade_info)

        # for i in range(len(driver.find_elements_by_css_selector("div.product")) - len(driver.find_elements_by_css_selector("div.product.disabled.toggledOff"))):
        #     if i >= len(product_info[0]):
        #         product_info[0].append(parse(find("productPrice" + str(i)).text))
        #         product_info[1].append(7*product_info[1][-1])
        #         product_info[2].append("???")

        for j in range(2):
            temp = product_info if j == 0 else upgrade_info
            for i, tooltip in enumerate(tooltips[j]):
                tooltip = tooltip.split("\n")
                if len(tooltip) > 3 and tooltip[1] != "[Achievement] [Locked]":
                    price = parse(tooltip.pop(0))
                    name = tooltip.pop(0)
                    if i >= len(temp[0]):
                        temp[0].append(price)
                        temp[2].append(name)
                    else:
                        temp[0][i] = price
                        temp[2][i] = name
                    tooltip.pop(0)
                    if j == 0:
                        if i >= len(temp[1]):
                            temp[1].append(parse(str(7*temp[1][i - 1]), float))
                        else:
                            if len(tooltip) > 1:
                                temp[1][i] = parse(tooltip[1].split()[4], float)
                    else:
                        value = 0
                        words = [name.lower() for name in product_info[2]] + ["mouse"]
                        numwords = {"twice" : 2}
                        descr = tooltip[0].lower()
                        num = 0
                        for key in numwords:
                            if key in descr:
                                num = numwords[key]
                        for word in words:
                            if word in descr:
                                if word == "mouse":
                                    value += num*rate*cookies_a_click
                                else:
                                    x = product_info[2].index(word[0].upper() + word[1:])
                                    value += (num - 1)*cps(x)*get_num(x)
                        temp[1].append(value)

        current_cookies, current_cps, cookies_a_click = cookies(), cps(), cookies_per_click()
        i = 0
        choice = max([i for i in range(products + 1)], key=lambda x: h(x))
        if upgrades > 0 and h(choice) < max(h(i, 1) for i in range(upgrades)):
            choice, i = max([i for i in range(upgrades)], key=lambda x: h(x, 1)), 1

        print(info)
        print("Buildings:")
        for j in range(2):
            if j == 1: print("Upgrades:")
            for i in range(len(info[j][0])):
                print("Name: {}; Cookies: {}; CPS: {}; Heuristic: {}".format(info[j][2][i], cookies(i, j), str(cps(i, j))[:str(cps(i, j)).index(".") + 3], h(i, j)))

        try:
            name = product_info[2][choice] if i == 0 else upgrade_info[2][choice]
        except IndexError:
            name = "???"
        cprint("Name: " + name, 'red', end='\n')
        cookie_clicker(choice, i)
        cprint("Current cookies in bank: " + str(cookies()), 'blue', end='\n')
        cprint("Current cookies per second (CPS): {}".format(round(current_cps, 2)), 'green', end='\n')
        cprint("Guesstimated rate: {}; Cookies/click: {}; CPS from mouse: {}".format(round(rate, 2), cookies_a_click, round(rate*cookies_a_click, 2)), 'green', end='\n')
        find(("product" if i == 0 else "upgrade") + str(choice)).click()
        close_notifs() #buggy af

    driver.close()
