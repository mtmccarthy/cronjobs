from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from typing import Dict, Tuple, Any
import gspread
from datetime import datetime
from googlemaps import Client, directions, googlemaps

from oauth2client.service_account import ServiceAccountCredentials


def get_location(addr: str) -> Tuple[float, float]:
    gmaps = get_gmaps()
    resp = gmaps.geocode(addr)
    loc = resp[0]['geometry']['location']
    return loc['lat'], loc['lng']


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
        'uberXL': get_low_high_estimates(prices[3]),
        'uberBLACK': get_low_high_estimates(prices[4]),
        'uberWAV': get_low_high_estimates(prices[5])
    }


def get_low_high_estimates(price: Dict[str, Any]) -> Tuple[float, float]:
    return float(price['low_estimate']), float(price['high_estimate'])


def get_gmaps():
    maps_key = "AIzaSyC4N2CrBVCXL9IXAJJim-Rn5xLM3sl-d2s"  # Restricted key, can only be run from my server.
    return googlemaps.Client(key=maps_key)


def main():
    gmaps = get_gmaps()

    franklin_str = '152 Franklin St, Stoneham, MA'

    silicon_str = '343 Congress St, Boston, MA'

    franklin_street = get_location(franklin_str)
    silicon_labs = get_location(silicon_str)

    dt = datetime.now()

    directions_home_to_work_transit = gmaps.directions(franklin_str, silicon_str, mode="transit", departure_time=dt)
    directions_work_to_home_transit = gmaps.directions(silicon_str, franklin_str, mode="transit", departure_time=dt)

    directions_home_to_work_driving = gmaps.directions(franklin_str, silicon_str, mode="driving", departure_time=dt)
    directions_work_to_home_driving = gmaps.directions(silicon_str, franklin_str, mode="driving", departure_time=dt)

    duration_home_to_work_transit = directions_home_to_work_transit[0]['legs'][0]['duration']
    duration_home_to_work_driving = directions_home_to_work_driving[0]['legs'][0]['duration']
    duration_work_to_home_transit = directions_work_to_home_transit[0]['legs'][0]['duration']
    duration_work_to_home_driving = directions_work_to_home_driving[0]['legs'][0]['duration']

    home_to_work_prices = get_price_estimate(franklin_street[0], franklin_street[1], silicon_labs[0], silicon_labs[1])
    work_to_home_prices = get_price_estimate(silicon_labs[0], silicon_labs[1], franklin_street[0], franklin_street[1])

    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client-secret.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('Uber Pricing').sheet1

    # Home to Work
    num_rows = len(sheet.get_all_records())  # 0 means no data, but labels in first row
    strRowNum = str((num_rows + 2))

    wth_auto_price_low = work_to_home_prices['uberx'][0]
    wth_auto_price_high = work_to_home_prices['uberx'][1]
    wth_auto_price_avg = (wth_auto_price_high + wth_auto_price_low)/2
    htw_auto_price_low = home_to_work_prices['uberx'][0]
    htw_auto_price_high = home_to_work_prices['uberx'][1]
    htw_auto_price_avg = (htw_auto_price_high + htw_auto_price_low)/2
    transit_price = 3.95 # Bus and Charlie ticket one way
    htw_hours_transit = duration_home_to_work_transit['value']/(3600*24)  # Percentage of a day from seconds
    htw_hours_driving = duration_home_to_work_driving['value']/(3600*24)
    wth_hours_transit = duration_work_to_home_transit['value']/(3600*24)
    wth_hours_driving = duration_work_to_home_driving['value']/(3600*24)

    htw_price_diff = htw_auto_price_avg - transit_price
    htw_time_diff = htw_hours_transit - htw_hours_driving

    wth_price_diff = wth_auto_price_avg - transit_price
    wth_time_diff = wth_hours_transit - wth_hours_driving

    sheet.update_acell('A' + strRowNum, dt)  # Datetime
    sheet.update_acell('B' + strRowNum, wth_price_diff)  # WTH Price Difference
    sheet.update_acell('C' + strRowNum, wth_time_diff)  # WTH Time Difference
    sheet.update_acell('D' + strRowNum, htw_price_diff)  # HTW Price Difference
    sheet.update_acell('E' + strRowNum, htw_time_diff)  # HTW Time Difference
    sheet.update_acell('F' + strRowNum, wth_auto_price_avg)  # WTH Auto Price
    sheet.update_acell('G' + strRowNum, transit_price)  # WTH Transit Price
    sheet.update_acell('H' + strRowNum, htw_auto_price_avg)  # HTW Auto Price
    sheet.update_acell('I' + strRowNum, transit_price)  # HTW Transit Price
    sheet.update_acell('J' + strRowNum, wth_hours_driving)  # WTH Auto Time
    sheet.update_acell('K' + strRowNum, wth_hours_transit)  # WTH Transit Time
    sheet.update_acell('L' + strRowNum, htw_hours_driving)  # HTW Auto Time
    sheet.update_acell('M' + strRowNum, htw_hours_transit)  # HTW Transit Time
    sheet.update_acell('N' + strRowNum, wth_auto_price_low)  # WTH Auto Low
    sheet.update_acell('O' + strRowNum, wth_auto_price_high)  # WTH Auto High
    sheet.update_acell('P' + strRowNum, htw_auto_price_low)  # HTW Auto Low
    sheet.update_acell('Q' + strRowNum, htw_auto_price_high)  # HTW Auto High

if __name__ == '__main__':
    main()
