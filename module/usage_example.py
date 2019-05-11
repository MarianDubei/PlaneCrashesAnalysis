from module.accidentdata import AccidentData

accidents = AccidentData("year", "2019")
accidents.get_data()
print(len(accidents))
print(accidents)
