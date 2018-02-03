from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from typing import Dict, Tuple, Any
import gspread
from datetime import datetime

from oauth2client.service_account import ServiceAccountCredentials


def get_price_estimate(slat: float, slong: float, elat: float, elong: float) -> Dict[str, Tuple[float, float]]:
    session = Session(server_token="KbuxOrEu9AkbguU1lPdne9wmc7q_qCHJJFlKHFLA")
    client = UberRidesClient(session)

    estimate = client.get_price_estimates(
        start_latitude=slat,
        start_longitude=slong,
        end_latitude=elat,
        end_longitude=elong,
        seat_count=1
    )

    prices = estimate.json.get('prices')
    return {
        'uber_pool': get_low_high_estimates(prices[0]),
        'uberx': get_low_high_estimates(prices[1]),
        'uberSUV': get_low_high_estimates(prices[2]),
        'uberXL' : get_low_high_estimates(prices[3]),
        'uberBLACK' : get_low_high_estimates(prices[4]),
        'uberWAV': get_low_high_estimates(prices[5])
    }


def get_low_high_estimates(price: Dict[str, Any]) -> Tuple[float, float]:
    return float(price['low_estimate']), float(price['high_estimate'])


def main():
    franklin_street = (42.4755587, -71.0897706)
    silicon_labs = (42.3506141, -71.0515498)

    home_to_work_prices = get_price_estimate(franklin_street[0], franklin_street[1], silicon_labs[0], silicon_labs[1])
    work_to_home_prices = get_price_estimate(silicon_labs[0], silicon_labs[1], franklin_street[0], franklin_street[1])

    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client-secret.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('Uber Pricing').sheet1

    #Home to Work
    num_rows = len(sheet.get_all_records()) #0 means no data, but labels in first row
    strRowNum = str((num_rows + 2))

    sheet.update_acell('A'+ strRowNum, datetime.now())
    sheet.update_acell('B'+strRowNum, "Home")
    sheet.update_acell('C' + strRowNum, "Work")
    sheet.update_acell('D' + strRowNum, home_to_work_prices['uberx'][0])
    sheet.update_acell('E' + strRowNum, home_to_work_prices['uberx'][1])

    num_rows = len(sheet.get_all_records()) #0 means no data, but labels in first row
    strRowNum = str((num_rows + 2))

    #Work to Home
    sheet.update_acell('A'+ strRowNum, datetime.now())
    sheet.update_acell('B'+strRowNum, "Work")
    sheet.update_acell('C' + strRowNum, "Home")
    sheet.update_acell('D' + strRowNum, work_to_home_prices['uberx'][0])
    sheet.update_acell('E' + strRowNum, work_to_home_prices['uberx'][1])

if __name__ == '__main__':
    main()
