import requests


class TestHotel:
    def test_hotel_autocomplete(self, hotel_api):
        """Test the autocomplete endpoint with a valid name query parameter."""
        url = f"{hotel_api}/autocomplete?name=sea"
        response = requests.get(url)
        assert response.status_code == 200

        result = response.json()
        assert isinstance(result, list)
        assert len(result) == 25

    def test_hotel_all_filter(self, hotel_api):
        """Test filtering hotels with specific filters."""
        url = f"{hotel_api}/filter"
        hotel_filter = {
            "title": "Carrizo Plain National Monument",
            "name": "KCL Campground",
            "country": "United States",
            "city": "Santa Margarita",
            "state": "California",
            "description": "newly renovated",
        }

        expected_hotels = [
            {
                "title": "Carrizo Plain National Monument",
                "name": "KCL Campground",
                "country": "United States",
                "city": "Santa Margarita",
                "state": "California",
                "description": "The campground has a gravel road, pit toilets, corrals and water for livestock. There are some well established shade trees and the facilities have just been renovated to include new fire rings with BBQ grates, lantern poles, and gravel roads and tent platforms.  Tenters, and small to medium sized campers will find the KCL a good fit.",
            }
        ]

        response = requests.post(url, json=hotel_filter)
        assert response.status_code == 200

        result = response.json()
        assert result == expected_hotels

    def test_hotel_with_single_filter(self, hotel_api):
        """Test filtering hotels with a single description filter."""
        url = f"{hotel_api}/filter"
        hotel_filter = {"description": "newly renovated"}

        response = requests.post(url, json=hotel_filter)
        assert response.status_code == 200

        result = response.json()
        assert isinstance(result, list)
        assert len(result) > 2

    def test_hotel_single_filter_with_pagination(self, hotel_api):
        """Test filtering hotels with description, offset, and limit filters."""
        page_size = 3
        iterations = 3
        hotel_filter = {"description": "newly renovated"}
        all_hotels = set()

        for i in range(iterations):
            hotel_filter["offset"] = page_size * i
            url = f"{hotel_api}/filter?limit={page_size}&offset={page_size*i}"
            response = requests.post(url, json=hotel_filter)
            assert response.status_code == 200

            result = response.json()
            assert isinstance(result, list)
            assert len(result) <= page_size

            for hotel in result:
                all_hotels.add(hotel["name"])

        assert len(all_hotels) >= page_size * iterations
