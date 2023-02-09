import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator
from deep_translator import GoogleTranslator
from time import sleep

translator = Translator()

headers = {
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"}
# this function takes an identifier as input and returns the listing id of the financial product
# with that identifier. It uses the Requests library to send a POST request to the API of the website,
# and returns the id from the JSON response.
def get_listing_id(identifier):
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    url = "https://www.yourmoney.ch/ym/api/search?searchTerm={}"
    try:
        response = session.post(url.format(identifier), headers=headers).json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}. Retrying...")
        sleep(1)
        response = session.post(url.format(identifier), headers=headers).json()

    try:
        return response['data']['solidListings'][0]['id']['value']
    except (KeyError, IndexError):
        return "Not available"
# this function takes a listing id as input
# and returns the URL of the details page
# of the financial product with that id.
def get_urllinks(listing_id):
    query_url = "https://www.yourmoney.ch/ym/details/" + listing_id + "#Tab0"
    print(query_url)
    return [query_url]
#  this function takes a query URL and an identifier as input
# and returns a DataFrame with the data of the financial product
# with that identifier. It uses the Requests library to send a GET request
# to the URL and BeautifulSoup to parse the HTML content and extract the data.
def scrape_data(query_url,identifier):
    if "Data not available" in query_url:
        return pd.DataFrame({"Type": ["Not available"]})


    response = requests.get(query_url,headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    masterdata_table = soup.find("table", {"id": "master-data-table"})
    if masterdata_table is None:
        return pd.DataFrame({"ISIN": [identifier],"Type": ["Not available"]})


    masterdata_list = masterdata_table.find_all("tr")
    if interest_table := soup.find("table", {"id": "interest-charges-table"}):
        interestdata_list = interest_table.find_all("tr")
        concat_list = [x for list_ in (masterdata_list, interestdata_list) for x in list_]
        is_derivative = False
    elif eusip_table := soup.find("table", {"id": "eusipa-table"}):
        eusipdata_list = eusip_table.find_all("tr")[:3]
        concat_list = [x for list_ in (masterdata_list, eusipdata_list) for x in list_]
        is_derivative = True
    else:
        return pd.DataFrame({"ISIN": [identifier], "Type": ["Not available"]})

    data = {"ISIN": [identifier], "Type": ["Bond"] if not is_derivative else "Derivative"}

    for tr in concat_list:
        th = tr.find("th")
        td = tr.find("td")
        if td:
            data[th.text] = td.text

    return pd.DataFrame(data, index=[0])

with open("./yourMoneyPortfolio.txt") as file:
    lines = file.read().splitlines()

results = pd.DataFrame()

for identifier in lines:
    listing_id = get_listing_id(identifier)
    urls = get_urllinks(listing_id)
    for url in urls:
        df = scrape_data(url, identifier)
        if isinstance(df, str):
            continue
        results = pd.concat([results, df], ignore_index=True)

results.rename(columns={'Domicile':'Country of Incorporation', 'Amount':'Issue amount','CCY':'Currency','Interest (p.a.)':'Interest rate','Call by Holder':'Put'}, inplace=True)
filename = "YourMOney_refdata.xlsx"
results.to_excel(filename, index=False)
