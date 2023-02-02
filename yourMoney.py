import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"}
def get_listing_id(identifier):
    url = "https://www.yourmoney.ch/ym/api/search?searchTerm={}"
    response = requests.post(url.format(identifier)).json()
    return response['data']['solidListings'][0]['id']['value']

def get_urllinks(listing_id):
    query_url = "https://www.yourmoney.ch/ym/details/" + listing_id + "#Tab0"
    return [query_url]
def scrape_data(query_url):
    response = requests.get(query_url,headers=headers)
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

with open("./yourMoneyPortfolio.txt") as file:
    lines = file.read().splitlines()

#create an empt data frame to store results
results = pd.DataFrame()
#loop through each identifier
for identifier in lines:
    listing_id = get_listing_id(identifier)
    query_url = get_urllinks(listing_id)
    print(query_url)
    for url in query_url:
        df = scrape_data(url)
        #append each iteration's result to the results data frame
        results = pd.concat([results, df],ignore_index=True)


#data copy to filename
filename = "YourMOney_refdata.xlsx"
results.to_excel(filename, index=False)





