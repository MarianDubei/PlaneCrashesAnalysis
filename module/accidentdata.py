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
        return accidents_url

    def parse_accidents(self, accidents_url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=600x400")
        driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), chrome_options=chrome_options)
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
            type_caption = table.find("td", "caption", text="Type:")
            date_caption = table.find("td", "caption", text="Date:")
            if type_caption:
                type_desc = type_caption.parent.find("td", "desc").find("a").text
            else:
                type_desc = None
            if date_caption:
                date_desc = date_caption.nextSibling.text
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
        destroyed_dct = {}

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

            if accident.damage == "Destroyed" or accident.damage == "Substantial":
                if accident.phase not in destroyed_dct.keys():
                    destroyed_dct[accident.phase] = 1
                else:
                    destroyed_dct[accident.phase] += 1

        self.analysis_dct["accidents_number"] = len(self.accidents)
        self.analysis_dct["fatalities_percent"] = fatal_percent_sum / self.analysis_dct["accidents_number"]
        max_percent_phase = sorted(list(self.analysis_dct['phases'].items()), key=lambda x: x[1], reverse=True)[0][0]
        max_percent_phase_num = max(self.analysis_dct['phases'].values()) / sum(self.analysis_dct['phases'].values()) * 100
        self.analysis_dct["max_percent_phase"] = (max_percent_phase, max_percent_phase_num)
        max_destroyed_planes_phase = sorted(list(self.analysis_dct['phases'].items()), key=lambda x: x[1], reverse=True)[0]
        self.analysis_dct["destroyed_damage"] = max_destroyed_planes_phase

    def show_infographics(self):
        self.form_analysis_data()
        infographics_str = f"Number of accidents: {self.analysis_dct['accidents_number']}\n" \
                           f"Percent of fatalities: {self.analysis_dct['fatalities_percent']}\n" \
                           f"Max fatalities count: {self.analysis_dct['max_fatalities']}\n" \
                           f"Phases: {self.analysis_dct['phases']}\n" \
                           f"Aircraft damage: {self.analysis_dct['damage']}\n" \
                           f"Phase with most accidents: {self.analysis_dct['max_percent_phase']}\n" \
                           f"Phase with accidents with planes dealed destroyed or substantial damage: {self.analysis_dct['destroyed_damage']}\n"
        print(infographics_str)

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
    category = input("Enter category: ")
    obj = input(f"Enter {category}: ")
    accidents = AccidentData(category, obj)
    accidents.get_data()
    accidents.show_infographics()
