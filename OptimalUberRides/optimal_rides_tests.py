from OptimalUberRides.optimal_rides import *
import unittest


class TestValidateSpreadsheet(unittest.TestCase):
    def setUp(self):
        maps_key = "AIzaSyC4N2CrBVCXL9IXAJJim-Rn5xLM3sl-d2s"
        # Restricted key, can only be run from my server.
        self.gmaps = googlemaps.Client(key=maps_key)
        self.franklin_str = '152 Franklin St, Stoneham, MA'
        self.silicon_str = '343 Congress St, Boston, MA'
        self.franklin_street = self.gmaps.geocode(self.franklin_str)
        self.silicon_labs = self.gmaps.geocode(self.silicon_str)


class TestAddressStrToLatLng(unittest.TestCase):
    def setUp(self):
        self.franklin_str = '152 Franklin St, Stoneham, MA'
        self.silicon_str = '343 Congress St, Boston, MA'
        self.franklin_street = get_location(self.franklin_str)

    def test_get_location(self):
        franklin_lat = 42.4755587
        franklin_long = -71.0875819
        self.assertAlmostEqual(franklin_lat,
                               self.franklin_street[0], delta=.00001)
        self.assertAlmostEqual(franklin_long, self.franklin_street[1], delta=.0001)


class TestPriceEstimate(unittest.TestCase):
    pass


class TestDurationEstimate(unittest.TestCase):
    pass



if __name__ == '__main__':
    unittest.main()
