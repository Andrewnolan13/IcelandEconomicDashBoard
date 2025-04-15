import multiprocessing

from src.constants import ENDPOINTS
from src.deamon import DataRefresher

if __name__ == '__main__':
    alive = multiprocessing.Event()
    alive.set()

    economyEndPoint=ENDPOINTS.Efnahagur

    request_endpoints = [
        economyEndPoint.Prices_and_consumption.Consumer_price_index.CPI.Consumer_price_index_and_changes__base_1988_100, # this is just a url endpoint
        economyEndPoint.Employment_and_labour_productivity.Employment.Number_of_employed_persons__jobs_and_hours_worked_by_economic_activity_and_quarters__1991_to_2024, # as is this
        getattr(economyEndPoint.National_accounts.Gross_domestic_product,'National_accounts_-_quarterly').Quarterly_GDP_1995_to_2024, # the map to typable didn't work well for this one
        economyEndPoint.National_accounts.Financial_accounts.Money_and_credit.Weighted_average_interest_rates_of_commercial_banks_1960_to_2016,
    ]

    table_names = [
        'CPI',
        'Employment',
        'GDP',
        'Interest'
    ]

    for i,(endpoint,table_name) in enumerate(zip(request_endpoints,table_names)):
        process = DataRefresher(endpoint=endpoint, table_name=table_name, sleep_period=60, wait=i*2, alive_event=alive)
        process.start()