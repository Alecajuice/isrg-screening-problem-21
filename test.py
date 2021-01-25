import os
import sys
from get_all_tickers import get_tickers as gt
import subprocess
import re

EXCLUDED_SYMBOLS = ["CBO", "CBX", "CELG~", "GIX~", "AUUD", "AUUDW", "BIOTU", "BTNB", "BCACU", "JAQCU", "MVNR", "NLSP", "NLSPW", "SPEL"]

fields = ["High", "Low", "Open", "Close"]
pattern = ""
for field in fields:
    pattern += field + ": [\d,]*\d(\.\d+)?\s*" # Output must be a number

symbols = gt.get_tickers()

print(symbols)

errored_symbols = []
for i in range(len(symbols)):
    symbol = symbols[i].strip()
    if symbol in EXCLUDED_SYMBOLS:
        continue
    try:
        out = subprocess.check_output(["py", "scrape.py", symbol]) # Expensive
        if not re.match(pattern, out.decode('utf8')):
            print("Output for symbol " + symbol + " is NaN", file=sys.stderr)
            errored_symbols.append(symbol)
    except subprocess.CalledProcessError as e:
        print("Error when fetching data for symbol " + symbol, file=sys.stderr)
        errored_symbols.append(symbol)
    print(str(i) + "/" + str(len(symbols)) + str(errored_symbols))

print("Errored on symbols " + str(errored_symbols))