# Python Stock Price Scraper
## Prompt
Write a Python application that can scrap stock price data from a public
website (e.g. yahoo finance,
https://finance.yahoo.com/quote/ISRG/history?p=ISRG) so that when given
a stock tick symbol (e.g. “ISRG”, aka Intuitive Surgical) as the input, the
application returns the stock’s high, low, open and close prices today.

Notes:
* You are allowed to use 3rd party Python modules but please be sure to define
the dependencies properly (e.g. via requirements.txt)
* Extra credits (optional):
  * exception handling (of corner cases),
  * accompanying test scripts,
  * design documentation (README.md),
  * architecture diagrams
  
## Usage
```
python scrape.py ISRG
```
to look up prices for ISRG.
```
python test.py
```
to run the test script.

## Important files
* `README.md` (this file): Contains documentation and architecture diagram
* `scrape.py`: scraper script
* `test.py`: test script
  
## Design
Goals:
* Fast - can run the script many times to scrape many symbols quickly
* Robust against changes to the source website
* Always exits with code 1 and an error message if an error occurs, otherwise exits with code 0

![Architecture Diagram](./architecture_diagram.png?raw=true)

One of the simplest ways to scrape data from a website is by using an HTML parser. For the purposes of this assignment, I chose [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) because it is simple to use, although in a practical situation, it may be necessary to choose a faster parser. By running the server response (which we get by using `requests`) through the parser, it becomes simple to traverse the structure of the website in order to find the data we need.

![Table](./table.png?raw=true)

Rather than traversing the structure of the entire website, which would be very suceptible to changes in the website structure, we look for a more direct way to find our data. The website currently uses a `table` element with the attribute `data-test="historical-prices"` to store the data we need. The data is stored in rows for each date, from most recent to least recent, with columns for each price field. To access the data, we simply use Beautiful Soup's `find` and `findAll` methods to query our parsed response to find the table and access its first row, which contains the data we want.

In order to be robust against changes in the ordering of the columns, the script looks in the header row for each price field we are looking for, and finds the column indices that match each price field. For example, it looks for the column marked "Open", finds that it is the 1st column, and uses that column index to find the data in the first row. This way, if the order of the columns on the website is changed, the script should still work. To match the text in the columns, we use Python's regular expression package to make sure the first alphabetical characters in the string match the field text. This is to be robust against changes to the column names that add asterisks, notes in parentheses, or other special characters. The data is then printed to `stdout`.

Throughout the script, error checking is put in place to catch errors, such as in requesting the page and finding elements in the parsed website. If the behavior of the program is not expected, the script returns with exit code 1 and prints an error message to `stderr`. Otherwise, the behavior is intended and it returns with exit code 0.

## Testing

In order to thoroughly test the scraper, we use the [get-all-tickers](https://github.com/shilewenuw/get_all_tickers) library to get a comprehensive list of all ticker symbols. We then run the scraping algorithm with each one of these symbols and use regular expressions to check that the output is following the expected format, and that the data scraped from the website is not NaN.

Currently, the test script runs fairly slowly due to the overhead of creating subprocesses, but in this case it actually works in our favor, since we cannot send too many requests to the Yahoo Finance page anyway, or it will return a 503 server error. Also, there is a short list of symbols in the get-all-tickers list that Yahoo Finance does not recognize — these are removed from the list manually.

## Conclusion
In practice, using an HTML parser to scrape data is prone to break when the website being scraped is changed, since the structure of the page or tag attributes (like the `data-test="historical-prices"` tag we are currently relying on to find the table) may change. A more robust way to fetch data like this is to use an API developed by the data provider. Since APIs are designed to be used by third-party applications, they should not change the structure of their data. A version number is provided in requests to the API so that when the API is changed, older versions of the API may still be supported, or if an older version is deprecated, an error message can be provided in the response so the third-party application does not silently fail.

Using an API also permits collection of data for a larger amount of symbols. Rather than sending one request for each individual symbol, a single request can get data for any number of symbols, reducing load on both the server and the client. Currently, if too many requests are sent to the Yahoo Finance server, they are rejected with a 503 server error.

In addition, using a scraper makes it hard to detect an error state. I was not able to find an easy way to differentiate between an error due to the site layout changing and an error due to the stock ticker symbol being invalid, since the website dynamically inserts error messages into the HTML. Therefore, I had to jumble both cases into a single error message. If an API was used, it is likely there would be a simple and robust way to check if the ticker symbol is valid.