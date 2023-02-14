# yourMoney-scraper
Scrape ref data of Bonds using Python from yourMoney
##
base url with isin :https://www.yourmoney.ch/ym/search/extended?searchTerm=ES0413211071
base url : https://www.yourmoney.ch/ym/search/extended?searchTerm={isin}
### Project Description
The purpose of the project is to scrape financial data (Bonds, Derivatives) from a website, yourmoney.ch, and then write the data to an Excel file.

The script uses the following libraries:

Requests: to send HTTP requests and fetch the data from the website
BeautifulSoup: to parse the HTML content of the website and extract the data
Pandas: to store the data in a DataFrame, a two-dimensional labeled data structure, and write it to an Excel file
Googletrans: to translate the data from one language to another
deep_translator: to translate the data using the GoogleTranslator
time: to add a delay to the execution of the script

### Learning throught this project

Understanding the use of the Requests and BeautifulSoup libraries, 
And the structure of the DataFrame in Pandas.
