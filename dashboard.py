import multiprocessing
from signal import signal
from signal import SIGINT, SIGTERM
import os

from src.constants import ENDPOINTS
from src.deamon import DataRefresher
from src.browser import EdgeLauncherThread
from src.app import app

#listener for CTRL+SHIFT+C to kill this process
def signal_handler(sig, frame):
    print("Received signal to terminate. Exiting...")
    for process in multiprocessing.active_children():
        process.terminate()
    os.system("taskkill /f /pid {}".format(os.getpid()))
signal(SIGINT, signal_handler)

def start_processes():
    '''
    Start a few processes to request from the api and write to the database in the background. 
    '''
    alive = multiprocessing.Event()
    alive.set()

    economyEndPoint=ENDPOINTS.Efnahagur
    populationEndPoint=ENDPOINTS.Ibuar

    request_endpoints = [
        economyEndPoint.Prices_and_consumption.Consumer_price_index.CPI.Consumer_price_index_and_changes__base_1988_100, # this is just a url endpoint
        economyEndPoint.Employment_and_labour_productivity.Employment.Number_of_employed_persons__jobs_and_hours_worked_by_economic_activity_and_quarters__1991_to_2024, # as is this
        getattr(economyEndPoint.National_accounts.Gross_domestic_product,'National_accounts_-_quarterly').Quarterly_GDP_1995_to_2024, # the map to typable didn't work well for this one
        economyEndPoint.National_accounts.Financial_accounts.Money_and_credit.Weighted_average_interest_rates_of_commercial_banks_1960_to_2016,
        populationEndPoint.Population.Overview.Quarterly_data.Births__deaths_and_migration_by_sex_and_citizenship__NUTS3_regions_and_quarters_2011_to_2024,
        populationEndPoint.Population.Overview.Quarterly_data.Population_by_municipality__sex__citizenship_and_quarters_2011_to_2024,
        populationEndPoint.Population.Overview.Overview.Population_by_sex_and_age_1841_to_2025        
    ]

    table_names = [
        'CPI',
        'Employment',
        'GDP',
        'Interest',
        'Flux',
        'Population_by_municipality',
        'Population'
    ]

    processes = []
    for i,(endpoint,table_name) in enumerate(zip(request_endpoints,table_names)):
        process = DataRefresher(endpoint=endpoint, table_name=table_name, sleep_period=60, wait=10+2*i, alive_event=alive)
        processes.append(process)

    for process in processes:
        process.start()
        print(f"Started process {process.name} with PID {process.pid} for endpoint {process.endpoint}")

    return processes

if __name__ == '__main__':
    # start the data requesting procesess
    processes = start_processes() # returning because I don't them to be garbage collected
    print("serving")
    # launch the browser
    try:
        edgeLauncherThread = EdgeLauncherThread()
        edgeLauncherThread.start()
    except Exception as e:
        print(f"Error starting EdgeLauncherThread: {e}")
        print("Please ensure that the Edge WebDriver is correctly installed and in PATH.")
        print("alternatively, just go to http://127.0.0.1:8050/ in your browser")
        print("The dashboard will continue to run in the background.")
    print("Launching Edge browser...")
    # begin hosting the dashboard
    app.run_server(debug=True, use_reloader=False)     

