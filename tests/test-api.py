import unittest
from unittest.mock import patch, MagicMock
from src.api import WeatherAPI

class TestWeatherAPI(unittest.TestCase):
    def setUp(self):
        self.api = WeatherAPI("https://api-open.data.gov.sg/v2/real-time/api")

    @patch('src.api.requests.get')
    def test_get_rainfall_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test_data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.api.get_rainfall_data()
        self.assertEqual(result, {"data": "test_data"})

    def test_parse_rainfall_data(self):
        test_data = {
            "data": {
                "stations": [
                    {
                        "id": "S1",
                        "name": "Station 1",
                        "labelLocation": {"latitude": 1.0, "longitude": 103.0}
                    }
                ],
                "readings": [
                    {
                        "data": [
                            {"stationId": "S1", "value": 5.0}
                        ]
                    }
                ]
            }
        }

        expected_result = {
            "S1": {
                "value": 5.0,
                "lat": 1.0,
                "lon": 103.0,
                "name": "Station 1"
            }
        }

        result = self.api.parse_rainfall_data(test_data)
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
