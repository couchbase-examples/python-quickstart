import requests
import pytest
from couchbase.exceptions import DocumentNotFoundException

"""How to Run Unit Tests
python -m pytest"""


class TestAirport:
    def test_add_airport(
        self, couchbase_client, airport_api, airport_collection, helpers
    ):
        """Test the successful creation of an airport"""
        airport_data = {
            "airportname": "Test Airport",
            "city": "Test City",
            "country": "Test Country",
            "faa": "TAA",
            "icao": "TAAS",
            "tz": "Europe/Berlin",
            "geo": {"lat": 40, "lon": 42, "alt": 100},
        }
        document_id = "airport_test_insert"
        helpers.delete_existing_document(
            couchbase_client, airport_collection, document_id
        )
        response = requests.post(url=f"{airport_api}/{document_id}", json=airport_data)
        assert response.status_code == 201

        # Check document stored in DB is same as sent & clean up
        doc_in_db = couchbase_client.get_document(
            airport_collection, key=document_id
        ).content_as[dict]
        assert doc_in_db == airport_data
        couchbase_client.delete_document(airport_collection, key=document_id)

    def test_add_duplicate_airport(
        self, couchbase_client, airport_api, airport_collection, helpers
    ):
        """Test the failed creation of an airport due to an existing airport"""
        airport_data = {
            "airportname": "Test Airport",
            "city": "Test City",
            "country": "Test Country",
            "faa": "TAA",
            "icao": "TAAS",
            "tz": "Europe/Berlin",
            "geo": {"lat": 40, "lon": 42, "alt": 100},
        }
        document_id = "airport_test_duplicate"
        helpers.delete_existing_document(
            couchbase_client, airport_collection, document_id
        )
        response = requests.post(url=f"{airport_api}/{document_id}", json=airport_data)
        assert response.status_code == 201
        response = requests.post(url=f"{airport_api}/{document_id}", json=airport_data)
        assert response.status_code == 409
        couchbase_client.delete_document(airport_collection, key=document_id)

    def test_add_airport_without_required_fields(
        self, couchbase_client, airport_api, airport_collection
    ):
        """Test the creation of an airport without required fields"""
        airport_data = {
            "city": "Test City",
            "faa": "TAA",
            "tz": "Europe/Berlin",
        }
        document_id = "airport_test_invalid_payload"
        response = requests.post(url=f"{airport_api}/{document_id}", json=airport_data)
        assert response.status_code == 400
        response_data = response.json()
        assert (
            response_data["errors"]["airportname"]
            == "'airportname' is a required property"
        )
        assert response_data["errors"]["country"] == "'country' is a required property"
        assert response_data["message"] == "Input payload validation failed"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airport_collection, key=document_id)

    def test_read_airport(
        self, couchbase_client, airport_api, airport_collection, helpers
    ):
        """Test the reading of an airport"""
        airport_data = {
            "airportname": "Test Airport",
            "city": "Test City",
            "country": "Test Country",
            "faa": "TAA",
            "icao": "TAAS",
            "tz": "Europe/Berlin",
            "geo": {"lat": 40, "lon": 42, "alt": 100},
        }
        document_id = "airport_test_read"
        helpers.delete_existing_document(
            couchbase_client, airport_collection, document_id
        )
        couchbase_client.insert_document(
            airport_collection, key=document_id, doc=airport_data
        )

        response = requests.get(url=f"{airport_api}/{document_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == airport_data

        couchbase_client.delete_document(airport_collection, key=document_id)

    def test_read_invalid_airport(
        self, couchbase_client, airport_api, airport_collection, helpers
    ):
        """Test the reading of an invalid airport"""
        document_id = "airport_test_invalid_id"
        helpers.delete_existing_document(
            couchbase_client, airport_collection, document_id
        )
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airport_collection, key=document_id)
        response = requests.get(url=f"{airport_api}/{document_id}")
        assert response.status_code == 404

    def test_update_airport(
        self, couchbase_client, airport_api, airport_collection, helpers
    ):
        """Test updating an existing airport"""
        airport_data = {
            "airportname": "Test Airport",
            "city": "Test City",
            "country": "Test Country",
            "faa": "TAA",
            "icao": "TAAS",
            "tz": "Europe/Berlin",
            "geo": {"lat": 40, "lon": 42, "alt": 100},
        }
        document_id = "airport_test_update"
        helpers.delete_existing_document(
            couchbase_client, airport_collection, document_id
        )
        couchbase_client.insert_document(
            airport_collection, key=document_id, doc=airport_data
        )

        updated_airport_data = {
            "airportname": "Updated Airport",
            "city": "Updated City",
            "country": "Updated Country",
            "faa": "TAA",
            "icao": "TAAS",
            "tz": "Europe/Berlin",
            "geo": {"lat": 40, "lon": 42, "alt": 100},
        }

        response = requests.put(
            url=f"{airport_api}/{document_id}", json=updated_airport_data
        )
        assert response.status_code == 200
        updated_document = couchbase_client.get_document(
            airport_collection, key=document_id
        ).content_as[dict]
        updated_api_response = response.json()
        assert updated_api_response == updated_document

        couchbase_client.delete_document(airport_collection, key=document_id)

    def test_update_with_invalid_document(
        self, couchbase_client, airport_api, airport_collection
    ):
        """Test updating an airport with an invalid airport"""
        document_id = "airport_test_update_invalid_doc"
        updated_airport_data = {
            "city": "Updated City",
            "country": "Updated Country",
            "faa": "TAA",
            "icao": "TAAS",
            "tz": "Europe/Berlin",
            "geo": {"lat": 40, "lon": 42, "alt": 100},
        }

        response = requests.put(
            url=f"{airport_api}/{document_id}", json=updated_airport_data
        )
        assert response.status_code == 400

        response_data = response.json()
        assert (
            response_data["errors"]["airportname"]
            == "'airportname' is a required property"
        )
        assert response_data["message"] == "Input payload validation failed"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airport_collection, key=document_id)

    def test_delete_airport(
        self, couchbase_client, airport_api, airport_collection, helpers
    ):
        """Test deleting an existing airport"""
        airport_data = {
            "airportname": "Test Airport",
            "city": "Test City",
            "country": "Test Country",
            "faa": "TAA",
            "icao": "TAAS",
            "tz": "Europe/Berlin",
            "geo": {"lat": 40, "lon": 42, "alt": 100},
        }
        document_id = "airport_test_delete"
        helpers.delete_existing_document(
            couchbase_client, airport_collection, document_id
        )
        couchbase_client.insert_document(
            airport_collection, key=document_id, doc=airport_data
        )

        response = requests.delete(url=f"{airport_api}/{document_id}")
        assert response.status_code == 204

        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airport_collection, key=document_id)

    def test_delete_non_existing_airport(
        self, couchbase_client, airport_api, airport_collection, helpers
    ):
        """Test deleting a non-existing airport"""
        document_id = "airport_test_delete_non_existing"
        helpers.delete_existing_document(
            couchbase_client, airport_collection, document_id
        )
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airport_collection, key=document_id)
        response = requests.delete(url=f"{airport_api}/{document_id}")
        assert response.status_code == 404

    def test_list_airports(self, airport_api):
        """Test listing airports without specifying a country"""
        response = requests.get(url=f"{airport_api}/list")
        assert response.status_code == 200
        response_data = response.json()
        # Default page size
        assert len(response_data) == 10

    def test_list_airports_in_country(self, airport_api):
        """Test listing airports in a country"""
        country = "France"
        response = requests.get(url=f"{airport_api}/list?country={country}")
        assert response.status_code == 200
        response_data = response.json()
        for data in response_data:
            assert data["country"] == country

    def test_list_airports_in_country_with_pagination(self, airport_api):
        """Test listing airports in a country with pagination"""
        country = "France"
        page_size = 3
        iterations = 3
        airports_list = set()

        for i in range(iterations):
            response = requests.get(
                url=f"{airport_api}/list?country={country}&limit={page_size}&offset={page_size*i}"
            )
            assert response.status_code == 200
            response_data = response.json()
            assert len(response_data) == page_size
            for data in response_data:
                airports_list.add(data["airportname"])
                assert data["country"] == country
        assert len(airports_list) == page_size * iterations

    def test_list_airports_in_invalid_country(self, airport_api):
        """Test listing airports in an invalid country"""
        response = requests.get(url=f"{airport_api}/list?country=invalid")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 0

    def test_direct_connections(self, couchbase_client, airport_api):
        """Test the direct connections from an airport"""
        airport = "JFK"

        query = """
                SELECT distinct (route.destinationairport)
                FROM airport as airport
                JOIN route as route on route.sourceairport = airport.faa
                WHERE airport.faa = $airport and route.stops = 0
                ORDER BY route.destinationairport
            """
        result = couchbase_client.query(query, airport=airport)
        db_airports = [r for r in result]

        response = requests.get(
            url=f"{airport_api}/direct-connections?airport={airport}"
        )
        assert response.status_code == 200
        for item in response.json():
            assert item in db_airports
        assert response.status_code == 200

    def test_direct_connections_invalid_airport(self, airport_api):
        """Test the direct connections from an invalid airport"""
        airport = "invalid"
        response = requests.get(
            url=f"{airport_api}/direct-connections?airport={airport}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 0
