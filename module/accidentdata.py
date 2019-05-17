import requests
from bs4 import BeautifulSoup as bs
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from module.accident import Accident
import os
import plotly.offline as py
import plotly.graph_objs as go


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

        elif self.criteria_type == "airline":
            base_url = "https://aviation-safety.net/database/operator/airlinesearch.php"
            data = {"naam": self.criteria, "submit": "Search"}
            response = requests.post(base_url, data=data)
            soup = bs(response.content, "html.parser")
            accidents_url = "https://aviation-safety.net" + soup.find("a", text=re.compile(self.criteria))["href"]

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
        driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=chrome_options)
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
        self.analysis_dct["years"] = []
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

            self.analysis_dct["years"].append(accident.aircraft_years)

        self.analysis_dct["accidents_number"] = len(self.accidents)
        self.analysis_dct["fatalities_percent"] = fatal_percent_sum / self.analysis_dct["accidents_number"]
        max_percent_phase = sorted(list(self.analysis_dct['phases'].items()), key=lambda x: x[1], reverse=True)[0][0]
        max_percent_phase_num = max(self.analysis_dct['phases'].values()) / sum(self.analysis_dct['phases'].values()) * 100
        self.analysis_dct["max_percent_phase"] = (max_percent_phase, max_percent_phase_num)
        max_destroyed_planes_phase = sorted(list(self.analysis_dct['phases'].items()), key=lambda x: x[1], reverse=True)[0]
        self.analysis_dct["destroyed_damage"] = max_destroyed_planes_phase

    def show_infographics(self):
        self.form_analysis_data()

        def div_wrapper(content_str):
            start_str = '<div class="row mb-3"><div class="col-md-12">'
            end_str = '</div></div>'
            return start_str + content_str + end_str

        html_str = ""

        header_div = f'<h1 class="text-center">{self.criteria_type[0].upper()+self.criteria_type[1:]}: {self.criteria}</h1>'
        html_str += div_wrapper(header_div)

        accident_number = f'<h2><b>Number of accidents:</b> {self.analysis_dct["accidents_number"]}</h2>'
        html_str += div_wrapper(accident_number)

        fatalities_head = "<h2><b>Percentage of fatalities:</b></h2>"
        labels = ['Fatalities', ' ']
        percent = self.analysis_dct['fatalities_percent']
        values = [percent, 100 - percent]
        colors = ['#428bca', '#FFFFFF']
        trace = go.Pie(labels=labels, values=values, marker=dict(colors=colors))
        plot_str = py.plot([trace], output_type='div')
        html_str += div_wrapper(fatalities_head + plot_str)

        max_fatalities_count = f"<h2><b>Max fatalities count:</b> {self.analysis_dct['max_fatalities']}</h2>"
        html_str += div_wrapper(max_fatalities_count)

        phases_head = "<h2><b>Number of accidents in every phase:</b></h2><br><p>STD - Standing; TXI - Taxi;</p>" \
                      "<br><p>TOF - Takeoff; ICL - Initial climb;</p>" \
                      "<br><p>ENR - En route; MNV - Maneuvering;</p>" \
                      "<br><p>APR - Approach; LDG - Landing;</p>"
        phases = ['STD', 'TXI', 'TOF', 'ICL', 'ENR', 'MNV', 'APR', 'LDG']
        phase_accidents = []
        for phase in phases:
            if phase in self.analysis_dct['phases'].keys():
                phase_accidents.append(self.analysis_dct['phases'][phase])
            else:
                phase_accidents.append(0)
        phases_bars = go.Bar(x=phases, y=phase_accidents)
        phases_bars_str = py.plot([phases_bars], output_type='div')
        html_str += div_wrapper(phases_head + phases_bars_str)

        damage_head = "<h2><b>Number of accidents due to type of received damage:</b></h2>"
        damage_types = list(self.analysis_dct['damage'].keys())
        damage_accidents = list(self.analysis_dct['damage'].values())
        damage_bars = go.Bar(x=damage_types, y=damage_accidents)
        damage_bars_str = py.plot([damage_bars], output_type='div')
        html_str += div_wrapper(damage_head + damage_bars_str)

        max_phase_tuple = self.analysis_dct['max_percent_phase']
        max_percent_phase = f"<h2><b>Phase with most accidents:</b> {max_phase_tuple[0]} - {max_phase_tuple[1]} % of all accidents</h2>"
        html_str += div_wrapper(max_percent_phase)

        max_damage_tuple = self.analysis_dct['destroyed_damage']
        max_destroyed_aircrafts = f"<h2><b>Phase with most destroyed aircrafts:</b> {max_damage_tuple[0]} - {max_damage_tuple[1]}</h2>"
        html_str += div_wrapper(max_destroyed_aircrafts)
        aircrafts_years_head = "<h2><b>Numbers of years after first flight of destroyed aircrafts:</b></h2>"
        aircrafts_years = go.Bar(x=self.analysis_dct['years'], y=[str(i) for i in range(1, len(self.analysis_dct["years"]) + 1)], orientation='h')
        aircrafts_years_str = py.plot([aircrafts_years], output_type='div')
        html_str += div_wrapper(aircrafts_years_head + aircrafts_years_str)

        median_years = f"<h2><b>Mean value of years after first flight of destroyed aircrafts:</b> {sum(self.analysis_dct['years'])/len(self.analysis_dct['years'])} years</h2>"
        html_str += div_wrapper(median_years)
        return html_str

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
