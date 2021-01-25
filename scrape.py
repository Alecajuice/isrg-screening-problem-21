import sys
import requests
from bs4 import BeautifulSoup
import re

fields = ["High", "Low", "Open", "Close"]
patterns = ["^[^a-z]*" + field.lower() + ".*" for field in fields] # The first alphabetical characters in the string must match the field

def find(element, tag, attrs=None):
    if attrs is None:
        ret = element.find(tag)
    else:
        ret = element.find(tag, attrs)
    if ret is None:
        print("ERROR: Could not find " + tag + " in element. The symbol may not exist or the website layout may have changed.", file=sys.stderr)
        sys.exit(1)
    return ret

def findAll(element, tag, attrs=None):
    if attrs is None:
        ret = element.findAll(tag)
    else:
        ret = element.findAll(tag, attrs)
    if len(ret) < 1:
        print("ERROR: Could not find " + tag + " in element. The symbol may not exist or the website layout may have changed.", file=sys.stderr)
        sys.exit(1)
    return ret

# Read command line arguments
if len(sys.argv) < 2:
    print("Usage: py scrape.py [symbol]")
    sys.exit(0)
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
if not page: # Status code >400 (not OK)
    print("ERROR: Server responded with status code " + str(page.status_code), file=sys.stderr)
    sys.exit(1)

soup = BeautifulSoup(page.content, 'html.parser')
table = find(soup, "table", {"data-test" : "historical-prices"})

# Find field indices from the table header
head = find(table, "thead")
header_row = findAll(find(head, "tr"), "th")
field_indices = [None] * len(fields) # Preallocate for speed
for i in range(len(header_row)):
    col = header_row[i]
    text = find(col, "span").text.lower()
    for j in range(len(patterns)):
        pattern = patterns[j]
        if re.match(pattern, text):
            field_indices[j] = i

# Find values for each field
body = find(table, "tbody")
first_row = findAll(find(body, "tr"), "td")
for i in range(len(fields)):
    field = fields[i]
    ind = field_indices[i]
    if ind is None or ind >= len(first_row):
        print("ERROR: Field not found: " + field + ". The website layout may have changed.", file=sys.stderr)
    else:
        col = first_row[ind]
        print(field + ": " + find(col, "span").text)