# fundamentals-data-alpha-vantage

Evaluating fundamentals data is often a key step in picking good companies to invest your money in. Investors often care about operating margins, EBITA, ROE, revenue growth rate, liabilities, and other key metrics to determine a company's financial health. However, comparing fundamentals data between companies is often a tedious affair that is slow and time-consuming. I've written a Python script that uses the Alpha Vantage API to gather fundamentals data for any given list of companies and compile it into a CSV file for easy comparison.

This code requires you to register an account with Alpha Vantage and get an API key, additionally, I'm using the Alpha vantage library. You can easily install it using ```pip install alpha_vantage```. They offer a free plan, however, it has rate limits of a max of 5 api calls in a minute and 500 max daily. There are also paid subscription tiers that range from 75 to 1200 API calls per minute (all paid plans have unlimited daily calls). When you call the function you can customize for which plan you have. This script will sleep for 61 seconds between tickers, which adds up fast. If you are going to be comparing a lot of data or companies, I would recommend paying for the API.

This code is highly customizable, we first get all the data using the ```getAnnualData()``` function. This actually has all the data that we need but there's just too much to use. Some information simply isn't relevant for our purposes, the ```processData()``` function only keeps the metrics that we are interested in. I've put comments denoting which sections are processing which sections (company_overview, income_statement, balance_sheet, or cash_flow). My code is an example of metrics that I'm interested in, if you want to switch metrics go to the documentation here: https://www.alphavantage.co/documentation/#fundamentals. If you click on the example outputs linked below each section, you can see exactly which metrics are outputted and what they're called. (example for the company overview: https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo)

##Results

I wrote code to collect fundamentals data that I'm interested in when looking at companies. I wanted the following metrics:
```['Symbol', 'last_quote', 'AnalystTargetPrice', 'Sector',
       'MarketCapitalization', 'RevenueTTM', 'ReturnOnAssetsTTM',
       'ReturnOnEquityTTM', 'EBITDA', 'ProfitMargin', 'OperatingMarginTTM',
       'GrossProfitTTM', 'DividendYield', 'RevenueGrowth3YrPct',
       'COGSGrowth3YrPct', 'totalAssets', 'totalLiabilities',
       'cashAndShortTermInvestments', 'operatingCashflow',
       'capitalExpenditures']```



I attached the Python code and a CSV file of the corresponding output.

```python

from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd
import time
import yfinance as yf

key = 'YOUR_API_KEY_HERE'


def getAnnualData(ticker, apiKey):
    fd = FundamentalData(key=apiKey, output_format='pandas')
    overview, meta = fd.get_company_overview(symbol = ticker)
    income, meta = fd.get_income_statement_annual(symbol = ticker)
    balance, meta = fd.get_balance_sheet_annual(symbol = ticker)
    cashflow, meta = fd.get_cash_flow_annual(symbol = ticker)
    return overview, income, balance, cashflow

def processData(overview, income, balance, cashflow):
    #I used the yfinance library to get the current price of the stock,
    symbol = overview['Symbol'][0]
    stock = yf.Ticker(symbol)
    datas = stock.history()
    last_quote = datas['Close'].iloc[-1]
    row_data = pd.DataFrame({'Symbol': symbol, 'last_quote': last_quote}, index=[0])
#########################################################----Overview----#########################################################
    # Select required columns from overview
    overview_columns = ['AnalystTargetPrice', 'Sector', 'MarketCapitalization', 'RevenueTTM', 'ReturnOnAssetsTTM', 
                        'ReturnOnEquityTTM', 'EBITDA', 'ProfitMargin', 'OperatingMarginTTM',
                        'GrossProfitTTM', 'DividendYield']
    overview_df = overview[overview_columns].reset_index(drop=True)
    row_data = pd.concat([row_data, overview_df], axis=1)
    
#########################################################----Income----#########################################################
    # Calculate 3-year revenue growth rate
    try:
        if len(income['totalRevenue']) >= 4:
            initial_revenue = int(income['totalRevenue'][3])
            current_revenue = int(income['totalRevenue'][0])
            rev_growth_3y = (current_revenue - initial_revenue) / initial_revenue
        
    except Exception as e:
        print(f"Error calculating revenue growth: {e}")
        rev_growth_3y = None

    
    # Calculate 3-year Cost of Goods and Services(COGS) growth rate
    try:
        if len(income['costofGoodsAndServicesSold']) >= 4:
            initial_cogs = int(income['costofGoodsAndServicesSold'][3])
            current_cogs = int(income['costofGoodsAndServicesSold'][0])
            cogs_growth_3y = (current_cogs - initial_cogs) / initial_cogs
    except Exception as e:
        print(f"Error calculating cogs growth: {e}")
        cogs_growth_3y = None

    row_data['RevenueGrowth3YrPct'] = rev_growth_3y
    row_data['COGSGrowth3YrPct'] = cogs_growth_3y

#########################################################----Balance----#########################################################
    # Add selected balance values
    balance_columns = ['totalAssets', 'totalLiabilities', 'cashAndShortTermInvestments']
    row_data[balance_columns] = balance[balance_columns].iloc[0].reset_index(drop=True)

#########################################################----Cashflow----#########################################################

    # Add selected cashflow values
    cashflow_columns = ['operatingCashflow', 'capitalExpenditures']
    row_data[cashflow_columns] = cashflow[cashflow_columns].iloc[0].reset_index(drop=True)

    return row_data


def compareStocks(tickerList, apiKey, freeApi = False):
    allData = pd.DataFrame()
    for i in tickerList:
        overview, income, balance, cashflow = getAnnualData(i, apiKey)
        temp = pd.DataFrame(processData(overview, income, balance, cashflow))
        allData = pd.concat([allData,temp], ignore_index=True)

        #Since the free API only allows 5 calls per minute, we need to sleep for at least 60 seconds every loop
        if freeApi == True:
            time.sleep(61)
    allData.to_csv('compareTickers.csv', index=False)

tickList = ["MSFT", "AAPL", "NVDA", "AMZN", "META", "TSLA", "GOOG", "DIS", "BABA", "JPM", ]
compareStocks(tickList, key, freeApi=True)

```
