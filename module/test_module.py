import unittest
from module.accidentdata import AccidentData


class PlaneCrashTest(unittest.TestCase):
    def setUp(self):
        self.year_accidents = AccidentData("year", "1919")
        self.aircraft_accidents = AccidentData("aircraft", "Boeing 737-8 MAX")

    def test_data(self):
        self.year_accidents.get_data()
        self.aircraft_accidents.get_data()

        self.year_accidents.show_infographics()
        self.aircraft_accidents.show_infographics()

        self.assertEqual(self.year_accidents.criteria_type, "year")
        self.assertEqual(self.year_accidents.criteria, "1919")
        self.assertEqual(len(self.year_accidents), 2)
        self.assertEqual(self.year_accidents.analysis_dct["accidents_number"],
                         2)
        self.assertEqual(self.year_accidents.analysis_dct["max_fatalities"],
                         14)
        self.assertEqual(self.year_accidents.analysis_dct["phases"],
                         {'ENR': 1, 'ICL': 1})
        self.assertEqual(self.year_accidents.analysis_dct["damage"],
                         {'Destroyed': 1, 'Damaged beyond repair': 1})
        self.assertEqual(self.year_accidents.analysis_dct["max_percent_phase"],
                         ('ENR', 50.0))
        self.assertEqual(self.year_accidents.analysis_dct["destroyed_damage"],
                         ('ENR', 1))

        self.assertEqual(self.aircraft_accidents.criteria_type, "aircraft")
        self.assertEqual(self.aircraft_accidents.criteria, "Boeing 737-8 MAX")
        self.assertEqual(
            self.aircraft_accidents.analysis_dct["accidents_number"], 2)
        self.assertEqual(
            self.aircraft_accidents.analysis_dct["max_fatalities"], 189)
        self.assertEqual(self.aircraft_accidents.analysis_dct["phases"],
                         {'ENR': 2})
        self.assertEqual(self.aircraft_accidents.analysis_dct["damage"],
                         {'Destroyed': 2})
        self.assertEqual(
            self.aircraft_accidents.analysis_dct["max_percent_phase"],
            ('ENR', 100.0))
        self.assertEqual(
            self.aircraft_accidents.analysis_dct["destroyed_damage"],
            ('ENR', 2))


if __name__ == '__main__':
    unittest.main()
