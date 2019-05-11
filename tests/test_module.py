import unittest
from ..module.accidentdata import AccidentData


class PlaneCrashTest(unittest.TestCase):
    def setUp(self):
        self.year_accidents = AccidentData("year", "")
        self.country_accidents = AccidentData("country", "")
        self.aircraft_accidents = AccidentData("aircraft", "")
        self.airlines_accidents = AccidentData("airlines", "")

    def test_get_data(self):
        self.year_accidents.get_data()
        self.country_accidents.get_data()
        self.aircraft_accidents.get_data()
        self.airlines_accidents.get_data()

    def test_analysis_data(self):
        pass


if __name__ == '__main__':
    unittest.main()
