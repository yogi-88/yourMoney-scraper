import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    masterdata_table = soup.find("table", {"id": "master-data-table"})
    interest_table = soup.find("table", {"id": "interest-charges-table"})

    masterdata_list = masterdata_table.find_all("tr")
    interestdata_list = interest_table.find_all("tr")

    concat_list = [x for list_ in (masterdata_list, interestdata_list) for x in list_]
    data = {}
    for tr in concat_list:
        th = tr.find("th")
        td = tr.find("td")
        data[th.text] = td.text
    return pd.DataFrame(data, index=[0])

url = "https://www.yourmoney.ch/ym/details/2076518%2C4%2C814"
df = scrape_data(url)
filename = "YourMOney_refdata.xlsx"
df.to_excel(filename, index=False)

# url = "https://www.yourmoney.ch/ym/details/2076518%2C4%2C814"
# response = requests.get(url)
# soup = BeautifulSoup(response.text, "html.parser")


# Masterdata_table = soup.find("table", {"id": "master-data-table"})
# Interest_table = soup.find("table", {"id": "interest-charges-table"})

# Masterdata_list = Masterdata_table.find_all("tr")
# Interestdata_list = Interest_table.find_all("tr")

# concat_list = [x for list_ in (Masterdata_list, Interestdata_list) for x in list_]
# print(concat_list)
# data = {}
# for tr in concat_list:
#     th = tr.find("th")
#     td = tr.find("td")
#     data[th.text] = td.text
#
# print(data)

# df = pd.DataFrame(data, index=[0])







