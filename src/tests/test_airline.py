import requests
import pytest
from couchbase.exceptions import DocumentNotFoundException


class TestAirline:
    def test_add_airline(self, couchbase_client, airline_api, airline_collection):
        """Test the successful creation of an airline"""
        airline_data = {
            "name": "Sample Airline",
            "iato": "SAL",
            "icao": "SALL",
            "callsign": "SAM",
            "country": "Sample Country",
        }
        document_id = "airline_test_insert"
        response = requests.post(url=f"{airline_api}/{document_id}", json=airline_data)
        assert response.status_code == 201

        # Check document stored in DB is same as sent & clean up
        doc_in_db = couchbase_client.get_document(
            airline_collection, key=document_id
        ).content_as[dict]
        assert doc_in_db == airline_data
        couchbase_client.delete_document(airline_collection, key=document_id)

    def test_add_duplicate_airline(
        self, couchbase_client, airline_api, airline_collection
    ):
        """Test the failed creation of an airline due to an existing airline"""
        airline_data = {
            "name": "Sample Airline",
            "iato": "SAL",
            "icao": "SALL",
            "callsign": "SAM",
            "country": "Sample Country",
        }
        document_id = "airline_test_duplicate"
        response = requests.post(url=f"{airline_api}/{document_id}", json=airline_data)
        assert response.status_code == 201
        response = requests.post(url=f"{airline_api}/{document_id}", json=airline_data)
        assert response.status_code == 409
        couchbase_client.delete_document(airline_collection, key=document_id)

    def test_add_airline_without_required_fields(
        self, couchbase_client, airline_api, airline_collection
    ):
        """Test the creation of an airline without required fields"""
        airline_data = {
            "iato": "SAL",
            "icao": "SALL",
            "country": "Sample Country",
        }
        document_id = "airline_test_invalid_payload"
        response = requests.post(url=f"{airline_api}/{document_id}", json=airline_data)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["errors"]["name"] == "'name' is a required property"
        assert (
            response_data["errors"]["callsign"] == "'callsign' is a required property"
        )
        assert response_data["message"] == "Input payload validation failed"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airline_collection, key=document_id)

    def test_read_airline(self, couchbase_client, airline_api, airline_collection):
        """Test the reading of an airline"""
        airline_data = {
            "name": "Sample Airline",
            "iato": "SAL",
            "icao": "SALL",
            "callsign": "SAM",
            "country": "Sample Country",
        }
        document_id = "airline_test_read"
        couchbase_client.insert_document(
            airline_collection, key=document_id, doc=airline_data
        )

        response = requests.get(url=f"{airline_api}/{document_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == airline_data

        couchbase_client.delete_document(airline_collection, key=document_id)

    def test_read_invalid_airline(
        self, couchbase_client, airline_api, airline_collection
    ):
        """Test the reading of an invalid airline"""
        document_id = "airline_test_invalid_id"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airline_collection, key=document_id)
        response = requests.get(url=f"{airline_api}/{document_id}")
        assert response.status_code == 404

    def test_update_airline(self, couchbase_client, airline_api, airline_collection):
        """Test updating an existing airline"""
        airline_data = {
            "name": "Sample Airline",
            "iato": "SAL",
            "icao": "SALL",
            "callsign": "SAM",
            "country": "Sample Country",
        }
        document_id = "airline_test_update"
        couchbase_client.insert_document(
            airline_collection, key=document_id, doc=airline_data
        )

        updated_airline_data = {
            "name": "Updated Airline",
            "iato": "SAL",
            "icao": "SALL",
            "callsign": "SAM",
            "country": "Updated Country",
        }

        response = requests.put(
            url=f"{airline_api}/{document_id}", json=updated_airline_data
        )
        assert response.status_code == 200
        updated_document = couchbase_client.get_document(
            airline_collection, key=document_id
        ).content_as[dict]
        updated_api_response = response.json()
        assert updated_api_response == updated_document

        couchbase_client.delete_document(airline_collection, key=document_id)

    def test_update_with_invalid_document(
        self, couchbase_client, airline_api, airline_collection
    ):
        """Test updating an airline with an invalid airline"""
        document_id = "airline_test_update_invalid_doc"
        updated_airline_data = {
            "iato": "SAL",
            "icao": "SALL",
            "callsign": "SAM",
            "country": "Updated Country",
        }

        response = requests.put(
            url=f"{airline_api}/{document_id}", json=updated_airline_data
        )
        assert response.status_code == 400

        response_data = response.json()
        assert response_data["errors"]["name"] == "'name' is a required property"
        assert response_data["message"] == "Input payload validation failed"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airline_collection, key=document_id)

    def test_delete_airline(self, couchbase_client, airline_api, airline_collection):
        """Test deleting an existing airline"""
        airline_data = {
            "name": "Sample Airline",
            "iato": "SAL",
            "icao": "SALL",
            "callsign": "SAM",
            "country": "Sample Country",
        }
        document_id = "airline_test_delete"
        couchbase_client.insert_document(
            airline_collection, key=document_id, doc=airline_data
        )

        response = requests.delete(url=f"{airline_api}/{document_id}")
        assert response.status_code == 204

        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airline_collection, key=document_id)

    def test_delete_non_existing_airline(
        self, couchbase_client, airline_api, airline_collection
    ):
        """Test deleting a non-existing airline"""
        document_id = "airline_test_delete_non_existing"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(airline_collection, key=document_id)
        response = requests.delete(url=f"{airline_api}/{document_id}")
        assert response.status_code == 404

    def test_list_airlines_in_country(self, airline_api):
        """Test listing airlines in a country"""
        country = "United Kingdom"
        response = requests.get(url=f"{airline_api}/list?country={country}")
        assert response.status_code == 200
        response_data = response.json()
        for data in response_data:
            assert data["country"] == country

    def test_list_airlines_in_country_with_pagination(self, airline_api):
        """Test listing airlines in a country with pagination"""
        country = "United Kingdom"
        page_size = 3
        iterations = 3
        airlines_list = set()

        for i in range(iterations):
            response = requests.get(
                url=f"{airline_api}/list?country={country}&limit={page_size}&offset={page_size*i}"
            )
            assert response.status_code == 200
            response_data = response.json()
            assert len(response_data) == page_size
            for data in response_data:
                airlines_list.add(data["name"])
                assert data["country"] == country
        assert len(airlines_list) == page_size * iterations

    def test_list_airlines_in_invalid_country(self, airline_api):
        """Test listing airlines in an invalid country"""
        response = requests.get(url=f"{airline_api}/list?country=invalid")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 0

    def test_to_airport_connections(self, couchbase_client, airline_api):
        """Test the destination airports from an airline"""
        airport = "JFK"

        query = """
                SELECT air.callsign
                FROM (
                    SELECT DISTINCT META(airline).id AS airlineId
                    FROM route
                    JOIN airline ON route.airlineid = META(airline).id
                    WHERE route.destinationairport = $airport
                ) AS subquery
                JOIN airline AS air ON META(air).id = subquery.airlineId
                ORDER BY air.name
            """
        result = couchbase_client.query(query, airport=airport)
        db_airlines = [r["callsign"] for r in result]

        response = requests.get(url=f"{airline_api}/to-airport?airport={airport}")
        assert response.status_code == 200

        for item in response.json():
            assert item["callsign"] in db_airlines
        assert response.status_code == 200

    def test_to_airport_connections_invalid_airport(self, airline_api):
        """Test the direct connections from an invalid airline"""
        airport = "invalid"
        response = requests.get(url=f"{airline_api}/to-airport?airport={airport}")
        assert response.status_code == 200
        assert len(response.json()) == 0
