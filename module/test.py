# from urllib.parse import urlparse
# url = "https://aviation-safety.net/database/dblist.php?Year=2019"
# import spynner
# url=requests.get(url)
# print(url.json())
dct = {'LDG': 20, 'TOF': 4, 'ENR': 11, 'APR': 2, 'MNV': 1, 'TXI': 3, 'STD': 4, 'ICL': 2}
phases_lst = sorted(list(dct.items()), key=lambda x: x[1], reverse=True)

print(phases_lst)