import requests
import time
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import pandas as pd
from random import randint
from time import sleep
from datetime import datetime


yourMoney = []
dateTimeObj = datetime.now()
filename = f'yourMoney_ref_data_{dateTimeObj.strftime("%d%m%Y-%H%M")}.xlsx'
headers = {
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"}
def get_listing_id(identifier):
    session = requests.Session()
    retry = Retry(connect=8, backoff_factor=0.8)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    url = "https://www.yourmoney.ch/ym/api/search?searchTerm={}"
    try:
        response = session.post(url.format(identifier), headers=headers).json()
        sleep(randint(1, 5))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}. Retrying...")
        sleep(randint(1, 5))
        response = session.post(url.format(identifier), headers=headers).json()
        sleep(randint(1, 5))

    try:
        return response['data']['solidListings'][0]['id']['value']
    except (KeyError, IndexError):
        return "Not available"

def get_urllinks(listing_id):
    query_url = "https://www.yourmoney.ch/ym/details/" + listing_id + "#Tab0"
    print(query_url)
    return [query_url]

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
        if int_payment_table := soup.find("table", {"id": "interest-payment-table"}):
            intpayment_list = int_payment_table.find_all("tr")
            concat_list = [x for list_ in (masterdata_list, eusipdata_list, intpayment_list) for x in list_]
        else:
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
    print(identifier)
    Type = ""
    Issue_Date = ""

    listing_id = get_listing_id(identifier)
    urls = get_urllinks(listing_id)

    for url in urls:
        df = scrape_data(url, identifier)

        try:
            df['Issue Date'] = pd.to_datetime(df['Issue Date'], format='%m/%d/%Y').dt.strftime('%d/%m/%Y')
        except (KeyError, ValueError):
            df['Issue Date'] = pd.NaT
        try:
            df['Maturity Date'] = pd.to_datetime(df['Maturity Date'], format='%m/%d/%Y').dt.strftime('%d/%m/%Y')
        except (KeyError, ValueError):
            df['Maturity Date'] = pd.NaT
        try:
            df['Last Listing Date'] = pd.to_datetime(df['Last Listing Date'], format='%m/%d/%Y').dt.strftime(
                '%d/%m/%Y')
        except (KeyError, ValueError):
            df['Last Listing Date'] = pd.NaT
        try:
            df['temp'] = pd.to_datetime('2000/' + df['Interest Date'], format='%Y/%m/%d', errors='coerce')
            df['Interest Date'] = pd.to_datetime(df['Interest Date'], format='%m/%d/%Y', errors='coerce').fillna(
                df['temp'])
            df['Interest Date'] = df['Interest Date'].dt.strftime('%d/%m/%Y').apply(
                lambda x: x.replace('/2000', '') if isinstance(x, str) else x)
            df = df.drop('temp', axis=1)
        except (KeyError, ValueError):
            df['Interest Date'] = pd.NaT

        df['ISIN'] = [identifier]

        if isinstance(df, str):
            continue
        results = pd.concat([results, df], ignore_index=True)
        #print(results.columns)

       #print(results)
    yourmoney_dict = results.to_dict('list')
    #print(yourmoney_dict)
    df = pd.DataFrame(yourmoney_dict, columns=['ISIN', 'Type', 'Issuer', 'Name', 'Domicile', 'Issue Date',
                                               'Maturity Date', 'Last Listing Date', 'Issue Volume', 'Amount',
                                               'Issue Price',
                                               'Instr. Unit', 'Unit', 'Denomination', 'Redemption Amount', 'CCY',
                                               'Valor', 'Symbol',
                                               'Call by Holder', 'Call by Issuer', 'Eusipa Category', 'EUSIPA Class',
                                               'Product Class', 'Interest (p.a.)', 'Interest', 'Interest frequency',
                                               'Interest Date', 'Daycount Convention', 'Acc. Interest'])
    df.rename(columns={'Domicile': 'Country of Incorporation', 'Amount': 'Issue amount', 'CCY': 'Currency',
                       'Interest (p.a.)': 'Interest rate', 'Call by Holder': 'Put'}, inplace=True)
    df.to_excel(filename, index=False)







