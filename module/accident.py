import re
from datetime import datetime


class Accident:
    CURRENT_YEAR = datetime.now().year

    def __init__(self, data):
        self.aircraft = data[0]
        self.date = data[1]
        self.first_flight = data[2]
        self.airframe_hrs = data[3]
        self.fatalities = data[4]
        self.damage = data[5]
        self.phase = data[6]
        self.aircraft_years = 0
        self.fatalities_percent = 0

    def process_data(self):
        self.aircraft_years = Accident.CURRENT_YEAR - int(re.search(r"[0-9]{4}", self.first_flight).group(0))
        fatalities_list = re.findall(r"[0-9]+", str(self.fatalities))
        if not(fatalities_list[0] == '0'):
            self.fatalities_percent = int(fatalities_list[0]) / int(fatalities_list[1]) * 100
        self.fatalities = int(fatalities_list[0])
        self.damage = self.damage
        self.phase = re.search(r"\(\w{3}\)", self.phase).group(0)[1:-1]

    def __str__(self):
        return f"Aircraft: {self.aircraft}\nDate: {self.date}\nFirst flight: {self.first_flight_year}\nTotal airframe hrs: {self.airframe_hrs}\nFatalities: {self.fatalities}\nAircraft damage: {self.damage}\nPhase: {self.phase}\n"
