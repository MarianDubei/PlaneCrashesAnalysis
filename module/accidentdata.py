import requests
from bs4 import BeautifulSoup as bs
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from module.accident import Accident
import os


class AccidentData:
    """
    Class for representing the information about plane accidents.
    """
    def __init__(self, criteria_type, criteria):
        self.accidents = set()
        self.criteria_type = criteria_type
        self.criteria = criteria
        self.analysis_dct = {}

    def get_accidents_url(self):
        if self.criteria_type == "aircraft":
            base_url = "https://aviation-safety.net/database/type/"
            request = requests.get(base_url)
            base_url = "https://aviation-safety.net"
            soup = bs(request.content, 'html.parser')
            accidents_url = base_url + soup.find("a", text=self.criteria)["href"].replace("index", "database")

        elif self.criteria_type == "country":
            base_url = "https://aviation-safety.net/database/country/"
            request = requests.get(base_url)
            soup = bs(request.content, 'html.parser')
            accidents_url = base_url + soup.find("a", text=self.criteria)["href"]

        elif self.criteria_type == "airlines":
            base_url = "https://aviation-safety.net/database/operator/airlinesearch.php"
            data = {"naam": self.criteria, "submit": "Search"}
            response = requests.post(base_url, data=data)
            soup = bs(response.text, "html.parser")
            accidents_url = "https://aviation-safety.net/" + soup.find("a", text=re.compile(self.criteria))["href"]

        elif self.criteria_type == "year":
            base_url = "https://aviation-safety.net/database/"
            request = requests.get(base_url)
            soup = bs(request.content, 'html.parser')
            accidents_url = base_url + soup.find("a", text=self.criteria)["href"]
        else:
            return 1
        return accidents_url

    def parse_accidents(self, accidents_url):
        # options = Options()
        # options.headless = True
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=600x400")
        chrome_driver = os.getcwd() + "/chromedriver"
        driver = webdriver.Chrome(executable_path=chrome_driver,
                                  chrome_options=chrome_options)

        # driver = webdriver.Firefox()
        driver.get(accidents_url)
        html = driver.page_source
        accidents_soup = bs(html, 'html.parser')
        accidents_table = accidents_soup.find("table")
        links = accidents_table.find_all("a")
        hrefs = []

        for link in links:
            hrefs.append("https://aviation-safety.net" + link.get("href"))
        hrefs = hrefs[1:]
        for href in hrefs:
            driver.get(href)
            html = driver.page_source
            driver.back()

            soup = bs(html, 'html.parser')
            table = soup.find("table")
            if not table:
                continue
            type = table.find("td", "caption", text="Type:")
            date = table.find("td", "caption", text="Date:")
            if type:
                type_desc = type.parent.find("td", "desc").find("a").text
            else:
                type_desc = None
            if date:
                date_desc = date.nextSibling.text
            else:
                date_desc = None
            data = [type_desc, date_desc]

            for caption_text in ["First flight:", "Total airframe hrs:",
                                 "Total:", "Aircraft damage:", "Phase:"]:
                td = table.find("td", "caption", text=caption_text)
                if not td:
                    desc = None
                else:
                    desc = td.parent.find("td", "desc").text.strip()
                data.append(desc)
            if not data[2] or data[6] == "()":
                continue
            self.accidents.add(Accident(data))

    def get_data(self):
        """
        Finds information about necessary plane crashes to the set.
        :return: None
        """
        accidents_url = self.get_accidents_url()
        self.parse_accidents(accidents_url)

    def form_analysis_data(self):
        """
        :return:
        """
        fatal_percent_sum = 0
        self.analysis_dct["max_fatalities"] = 0
        self.analysis_dct["phases"] = {}
        self.analysis_dct["damage"] = {}

        for accident in self.accidents:
            accident.process_data()
            fatal_percent_sum += accident.fatalities_percent
            if accident.fatalities > self.analysis_dct["max_fatalities"]:
                self.analysis_dct["max_fatalities"] = accident.fatalities

            if accident.phase not in self.analysis_dct["phases"].keys():
                self.analysis_dct["phases"][accident.phase] = 1
            else:
                self.analysis_dct["phases"][accident.phase] += 1

            if accident.damage not in self.analysis_dct["damage"].keys():
                self.analysis_dct["damage"][accident.damage] = 1
            else:
                self.analysis_dct["damage"][accident.damage] += 1

        self.analysis_dct["accidents_number"] = len(self.accidents)
        self.analysis_dct["fatalities_percent"] = fatal_percent_sum / self.analysis_dct["accidents_number"]
        self.analysis_dct["max_percent_phase"]
        self.analysis_dct["destroyed_damage"]
        self.analysis_dct["substantial_damage"]

    def show_infographics(self):
        self.form_analysis_data()
        infographics_str = f"Number of accidents: {self.analysis_dct['accidents_number']}\n" \
                           f"Percent of fatalities: {self.analysis_dct['fatalities_percent']}\n" \
                           f"Max fatalities count: {self.analysis_dct['max_fatalities']}\n" \
                           f"Phases: {self.analysis_dct['phases']}\n" \
                           f"Aircraft damage: {self.analysis_dct['damage']}\n"

        print(infographics_str)
        """
        Number of accidents: 47
        Percent of fatalities: 0.0
        Phases: {'LDG': 20, 'TOF': 4, 'ENR': 11, 'APR': 2, 'MNV': 1, 'TXI': 3, 'STD': 4, 'ICL': 2}
        Aircraft damage: {'Substantial': 28, 'Damaged beyond repair': 3, 'Destroyed': 14, 'Minor': 1, 'None': 1}
        Max fatalities count: 157
        """

    def add(self, elem):
        self.accidents.add(elem)

    def modify(self, old_elem, new_elem):
        try:
            self.accidents.remove(old_elem)
            self.accidents.add(new_elem)
        except KeyError:
            return 1

    def remove(self, elem):
        try:
            self.accidents.remove(elem)
        except KeyError:
            return 1

    def __len__(self):
        return len(self.accidents)

    def __str__(self):
        accidents_str = ""
        for accident in self.accidents:
            accidents_str += "\n" + str(accident)
        return accidents_str


if __name__ == '__main__':
    # category = input("Enter category: ")
    category = "year"
    # object = input(f"Enter {category}: ")
    object = "2019"

    a = AccidentData(category, object)
    import time
    start = time.time()
    a.get_data()
    print(time.time() - start)
    start = time.time()
    a.show_infographics()
    print(time.time() - start)