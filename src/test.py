import requests
import pytest

"""How to Run Unit Tests
pytest test.py"""

BASE = "http://127.0.0.1:5000"
BASEURI = f"{BASE}/api/v1/profile"
BASESEARCHURI = f"{BASE}/api/v1/profile/profiles"


def test_health_check():
    """Test the health check end point"""
    response = requests.get(f"{BASE}/api/v1/healthcheck/")
    assert response.status_code == 200


def test_add_profile():
    """Test the successful creation of a user profile"""
    profile_data = {
        "firstName": "john",
        "lastName": "doe",
        "email": "john.doe@couchbase.com",
        "password": "password",
    }
    response = requests.post(url=BASEURI, json=profile_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["firstName"] == "john"
    assert response_data["lastName"] == "doe"
    assert response_data["email"] == "john.doe@couchbase.com"


def test_add_profile_without_email():
    """Test the creation of a user profile without email"""
    profile_data = {
        "firstName": "john",
        "lastName": "doe",
        "password": "password",
    }
    response = requests.post(url=BASEURI, json=profile_data)
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["errors"]["email"] == "'email' is a required property"


def test_add_profile_without_password():
    """Test the creation of a user profile without password"""
    profile_data = {
        "firstName": "john",
        "lastName": "doe",
        "email": "john.doe@couchbase.com",
    }
    response = requests.post(url=BASEURI, json=profile_data)
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["errors"]["password"] == "'password' is a required property"


def test_add_profile_without_email_and_password():
    """Test the creation of a user profile without email and password"""
    profile_data = {"firstName": "john", "lastName": "doe"}
    response = requests.post(url=BASEURI, json=profile_data)
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["errors"]["email"] == "'email' is a required property"
    assert response_data["errors"]["password"] == "'password' is a required property"


def test_get_user_profile_id():
    """Test getting a user profile by id"""
    profile_data = {
        "firstName": "john",
        "lastName": "doe",
        "email": "john.doe@couchbase.com",
        "password": "password",
    }
    response_creation = requests.post(url=BASEURI, json=profile_data)
    assert response_creation.status_code == 201
    id = response_creation.json()["pid"]

    response_get = requests.get(url=f"{BASEURI}/{id}")
    assert response_get.status_code == 200
    read_result = response_get.json()
    assert read_result["firstName"] == profile_data["firstName"]
    assert read_result["lastName"] == profile_data["lastName"]
    assert read_result["email"] == profile_data["email"]


def test_get_user_profile__invalid_id():
    """Test getting a user profile by invalid id"""
    id = 1234

    response_get = requests.get(url=f"{BASEURI}/{id}")
    assert response_get.status_code == 404
    assert response_get.text == '"Key not found"\n'


def test_update_user_profile():
    """Test updating a user profile"""
    profile_data = {
        "firstName": "john",
        "lastName": "doe",
        "email": "john.doe@couchbase.com",
        "password": "password",
    }
    response_creation = requests.post(url=BASEURI, json=profile_data)
    assert response_creation.status_code == 201
    id = response_creation.json()["pid"]

    updated_profile_data = {
        "firstName": "jane",
        "lastName": "doe",
        "email": "jane.doe@couchbase.com",
        "password": "password#",
    }
    response_update = requests.put(url=f"{BASEURI}/{id}", json=updated_profile_data)

    assert response_update.status_code == 200
    updated_profile = response_update.json()

    assert updated_profile["firstName"] == updated_profile_data["firstName"]
    assert updated_profile["lastName"] == updated_profile_data["lastName"]
    assert updated_profile["email"] == updated_profile_data["email"]


def test_delete_user_profile():
    """Test deleting a user profile"""
    profile_data = {
        "firstName": "john",
        "lastName": "doe",
        "email": "john.doe@couchbase.com",
        "password": "password",
    }
    response_creation = requests.post(url=BASEURI, json=profile_data)
    assert response_creation.status_code == 201
    id = response_creation.json()["pid"]

    response_delete = requests.delete(url=f"{BASEURI}/{id}")

    assert response_delete.status_code == 200
    assert response_delete.text == '"OK"\n'


def test_delete_invalid_user_profile():
    """Test deleting an invalid user profile"""
    id = 1234

    response_delete = requests.delete(url=f"{BASEURI}/{id}")

    assert response_delete.status_code == 404
    assert response_delete.text == '"Key does not exist"\n'


def test_search_match():
    """Test searching for a user profile that matches the search string"""
    profile_data = {
        "firstName": "john",
        "lastName": "doe",
        "email": "john.doe@couchbase.com",
        "password": "password",
    }
    response_creation = requests.post(url=BASEURI, json=profile_data)
    assert response_creation.status_code == 201

    search_term = "jo"
    search_response = requests.get(url=f"{BASESEARCHURI}?search={search_term}")
    assert search_response.status_code == 200
    results = search_response.json()

    # check if the results returned contain the search term in them
    for res in results:
        assert not (
            res["firstName"].find(search_term) == -1
            and res["lastName"].find(search_term) == -1
        )


def test_search_no_match():
    """Test searching for a user profile that does not match the search string"""
    search_term = "123"
    search_response = requests.get(url=f"{BASESEARCHURI}?search={search_term}")
    assert search_response.status_code == 200
    results = search_response.json()

    # check if the results returned contain the search term in them
    for res in results:
        assert (
            res["firstName"].find(search_term) == -1
            and res["lastName"].find(search_term) == -1
        )
