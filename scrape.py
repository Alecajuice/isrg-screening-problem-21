import sys
import requests
from bs4 import BeautifulSoup
import re

fields = ["High", "Low", "Open", "Close"]
patterns = ["^[^a-z]*" + field.lower() + ".*" for field in fields] # The first alphabetical characters in the string must match the field

# Read command line arguments
symbol = sys.argv[1]

# Request data and parse
URL = 'https://finance.yahoo.com/quote/' + symbol + '/history?p=' + symbol
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}
page = requests.get(URL, headers)
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find("table", {"data-test" : "historical-prices"})

# Find field indices from the table header
head = table.find("thead")
header_row = head.find("tr").findAll("th")
field_indices = [None] * len(fields) # Preallocate for speed
for i in range(len(header_row)):
    col = header_row[i]
    text = col.find("span").text.lower()
    for j in range(len(patterns)):
        pattern = patterns[j]
        if re.match(pattern, text):
            field_indices[j] = i

# Find values for each field
body = table.find("tbody")
first_row = body.find("tr").findAll("td")
for i in range(len(fields)):
    field = fields[i]
    ind = field_indices[i]
    col = first_row[ind]
    print(field + ": " + col.find("span").text)