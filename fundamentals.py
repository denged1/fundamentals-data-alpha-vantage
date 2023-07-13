from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd
import time

key = 'TYPE_YOUR_API_KEY_HERE'


def getAnnualData(ticker, apiKey):
    fd = FundamentalData(key=apiKey, output_format='pandas')
    overview, meta = fd.get_company_overview(symbol = ticker)
    income, meta = fd.get_income_statement_annual(symbol = ticker)
    balance, meta = fd.get_balance_sheet_annual(symbol = ticker)
    cashflow, meta = fd.get_cash_flow_annual(symbol = ticker)
    return overview, income, balance, cashflow

def processData(overview, income, balance, cashflow):
#########################################################----Overview----#########################################################
    # Select required columns from overview
    overview_columns = ['Symbol', 'Sector', 'AnalystTargetPrice', 'MarketCapitalization', 'RevenueTTM', 'ReturnOnAssetsTTM', 
                        'ReturnOnEquityTTM', 'EBITDA', 'ProfitMargin', 'OperatingMarginTTM',
                        'GrossProfitTTM', 'DividendYield']
    row_data = overview[overview_columns].reset_index(drop=True)
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

tickList = ["MSFT", "AAPL", "NVDA", "AMZN", "META"]
compareStocks(tickList, key, freeApi=True)
