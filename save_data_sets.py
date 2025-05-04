from src.constants import ENDPOINTS, SOURCE
from src.api import StatisticsIcelandAPI
from src.deamon import DataRefresher
import os

economyEndPoint=ENDPOINTS.Efnahagur
populationEndPoint=ENDPOINTS.Ibuar


# endpoints used in dashboard
request_endpoints = [
        economyEndPoint.Prices_and_consumption.Consumer_price_index.CPI.Consumer_price_index_and_changes__base_1988_100, # this is just a url endpoint
        economyEndPoint.Employment_and_labour_productivity.Employment.Number_of_employed_persons__jobs_and_hours_worked_by_economic_activity_and_quarters__1991_to_2024, # as is this
        getattr(economyEndPoint.National_accounts.Gross_domestic_product,'National_accounts_-_quarterly').Quarterly_GDP_1995_to_2024, # the map to typable didn't work well for this one
        economyEndPoint.National_accounts.Financial_accounts.Money_and_credit.Weighted_average_interest_rates_of_commercial_banks_1960_to_2016,
        populationEndPoint.Population.Overview.Quarterly_data.Births__deaths_and_migration_by_sex_and_citizenship__NUTS3_regions_and_quarters_2011_to_2024,
        populationEndPoint.Population.Overview.Quarterly_data.Population_by_municipality__sex__citizenship_and_quarters_2011_to_2024,
        populationEndPoint.Population.Overview.Overview.Population_by_sex_and_age_1841_to_2025        
    ]

# init api object
api = StatisticsIcelandAPI()
api.add_endpoints(request_endpoints)
reponses = api.request()

# get the data
dataFrames = {k:DataRefresher.processResponse(v) for k,v in reponses.items()}

# save them to /data/ as csv files
for k,v in dataFrames.items():
    v.to_csv(os.path.join(SOURCE.DATA.str,f'{k}.csv'), index=True)