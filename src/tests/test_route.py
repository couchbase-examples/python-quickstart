import requests
import pytest
from couchbase.exceptions import DocumentNotFoundException


class Testroute:
    def test_add_route(self, couchbase_client, route_api, route_collection):
        """Test the successful creation of an route"""
        route_data = {
            "airline": "SAF",
            "airline_id": "airline_sample",
            "sourceairport": "SFO",
            "destinationairport": "JFK",
            "stops": 0,
            "equipment": "CRJ",
            "schedule": [{"day": 0, "flight": "SAF123", "utc": "14:05:00"}],
            "distance": 1000.79,
        }
        document_id = "route_test_insert"
        response = requests.post(url=f"{route_api}/{document_id}", json=route_data)
        assert response.status_code == 201

        # Check document stored in DB is same as sent & clean up
        doc_in_db = couchbase_client.get_document(
            route_collection, key=document_id
        ).content_as[dict]
        assert doc_in_db == route_data
        couchbase_client.delete_document(route_collection, key=document_id)

    def test_add_duplicate_route(self, couchbase_client, route_api, route_collection):
        """Test the failed creation of an route due to an existing route"""
        route_data = {
            "airline": "SAF",
            "airline_id": "airline_sample",
            "sourceairport": "SFO",
            "destinationairport": "JFK",
            "stops": 0,
            "equipment": "CRJ",
            "schedule": [{"day": 0, "flight": "SAF123", "utc": "14:05:00"}],
            "distance": 1000.79,
        }
        document_id = "route_test_duplicate"
        response = requests.post(url=f"{route_api}/{document_id}", json=route_data)
        assert response.status_code == 201
        response = requests.post(url=f"{route_api}/{document_id}", json=route_data)
        assert response.status_code == 409
        couchbase_client.delete_document(route_collection, key=document_id)

    def test_add_route_without_required_fields(
        self, couchbase_client, route_api, route_collection
    ):
        """Test the creation of an route without required fields"""
        route_data = route_data = {
            "airline_id": "airline_sample",
            "destinationairport": "JFK",
            "stops": 0,
            "equipment": "CRJ",
            "schedule": [{"day": 0, "flight": "SAF123", "utc": "14:05:00"}],
            "distance": 1000.79,
        }
        document_id = "route_test_invalid_payload"
        response = requests.post(url=f"{route_api}/{document_id}", json=route_data)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["errors"]["airline"] == "'airline' is a required property"
        assert (
            response_data["errors"]["sourceairport"]
            == "'sourceairport' is a required property"
        )
        assert response_data["message"] == "Input payload validation failed"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(route_collection, key=document_id)

    def test_read_route(self, couchbase_client, route_api, route_collection):
        """Test the reading of an route"""
        route_data = {
            "airline": "SAF",
            "airline_id": "airline_sample",
            "sourceairport": "SFO",
            "destinationairport": "JFK",
            "stops": 0,
            "equipment": "CRJ",
            "schedule": [{"day": 0, "flight": "SAF123", "utc": "14:05:00"}],
            "distance": 1000.79,
        }
        document_id = "route_test_read"
        couchbase_client.insert_document(
            route_collection, key=document_id, doc=route_data
        )

        response = requests.get(url=f"{route_api}/{document_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == route_data

        couchbase_client.delete_document(route_collection, key=document_id)

    def test_read_invalid_route(self, couchbase_client, route_api, route_collection):
        """Test the reading of an invalid route"""
        document_id = "route_test_invalid_id"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(route_collection, key=document_id)
        response = requests.get(url=f"{route_api}/{document_id}")
        assert response.status_code == 404

    def test_update_route(self, couchbase_client, route_api, route_collection):
        """Test updating an existing route"""
        route_data = {
            "airline": "SAF",
            "airline_id": "airline_sample",
            "sourceairport": "SFO",
            "destinationairport": "JFK",
            "stops": 0,
            "equipment": "CRJ",
            "schedule": [{"day": 0, "flight": "SAF123", "utc": "14:05:00"}],
            "distance": 1000.79,
        }
        document_id = "route_test_update"
        couchbase_client.insert_document(
            route_collection, key=document_id, doc=route_data
        )

        updated_route_data = {
            "airline": "USAF",
            "airline_id": "airline_sample_updated",
            "sourceairport": "SFO",
            "destinationairport": "JFK",
            "stops": 0,
            "equipment": "CRJ",
            "schedule": [{"day": 0, "flight": "SAF123", "utc": "14:05:00"}],
            "distance": 1000.79,
        }

        response = requests.put(
            url=f"{route_api}/{document_id}", json=updated_route_data
        )
        assert response.status_code == 200
        updated_document = couchbase_client.get_document(
            route_collection, key=document_id
        ).content_as[dict]
        updated_api_response = response.json()
        assert updated_api_response == updated_document

        couchbase_client.delete_document(route_collection, key=document_id)

    def test_update_with_invalid_document(
        self, couchbase_client, route_api, route_collection
    ):
        """Test updating an route with an invalid route"""
        document_id = "route_test_update_invalid_doc"
        updated_route_data = {
            "airline_id": "airline_sample",
            "sourceairport": "SFO",
            "destinationairport": "JFK",
            "stops": 0,
            "equipment": "CRJ",
            "schedule": [{"day": 0, "flight": "SAF123", "utc": "14:05:00"}],
            "distance": 1000.79,
        }

        response = requests.put(
            url=f"{route_api}/{document_id}", json=updated_route_data
        )
        assert response.status_code == 400

        response_data = response.json()
        assert response_data["errors"]["airline"] == "'airline' is a required property"
        assert response_data["message"] == "Input payload validation failed"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(route_collection, key=document_id)

    def test_delete_route(self, couchbase_client, route_api, route_collection):
        """Test deleting an existing route"""
        route_data = {
            "airline": "SAF",
            "airline_id": "airline_sample",
            "sourceairport": "SFO",
            "destinationairport": "JFK",
            "stops": 0,
            "equipment": "CRJ",
            "schedule": [{"day": 0, "flight": "SAF123", "utc": "14:05:00"}],
            "distance": 1000.79,
        }
        document_id = "route_test_delete"
        couchbase_client.insert_document(
            route_collection, key=document_id, doc=route_data
        )

        response = requests.delete(url=f"{route_api}/{document_id}")
        assert response.status_code == 204

        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(route_collection, key=document_id)

    def test_delete_non_existing_route(
        self, couchbase_client, route_api, route_collection
    ):
        """Test deleting a non-existing route"""
        document_id = "route_test_delete_non_existing"
        with pytest.raises(DocumentNotFoundException):
            couchbase_client.get_document(route_collection, key=document_id)
        response = requests.delete(url=f"{route_api}/{document_id}")
        assert response.status_code == 404
