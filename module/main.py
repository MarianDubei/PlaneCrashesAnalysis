from accidentdata import AccidentData


if __name__ == '__main__':
    category = input("Enter category: ")
    obj = input("Enter {}: ".format(category))
    accidents = AccidentData(category, obj)
    accidents.get_data()
    accidents.show_infographics()
