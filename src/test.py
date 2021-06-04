import requests

# ##############################
# TODO:  make real unit tests  #
# ##############################

BASE = "http://127.0.0.1:5000"
BASEURI = BASE + "/api/v1/profile/"
BASESEARCHURI = BASE + "/api/v1/profiles"

profileData = {
    "firstName": "john", 
    "lastName": "doe", 
    "email": "john.doe@couchbase.com", 
    "password": "password"
}

response = requests.get(BASE + "/api/v1/healthCheck/")
responsePost = requests.post(url=BASEURI, json=profileData)

print("healthCheck:\n")
print("------------\n")
print (response.json())
print ("\n")

print("add profile:\n")
print("------------\n")
print (responsePost.json())
print ("\n")

#transform data with update
data = responsePost.json()
data["firstName"] = "Jane"
data["lastName"] = "Doe"
data["email"] = "jane.doe@couchbase.com"
data["password"] = "Password1"
postUri = BASEURI + data["pid"]
responsePut = requests.put(url=postUri, json=data)

print("update profile:\n")
print("------------\n")
print (responsePut)
print ("\n")


searchUri = f"{BASESEARCHURI}?search=jane&limit=5&skip=0"
print ("URL for Search: " + searchUri)
responseSearch = requests.get(url=searchUri)
print("------------\n")
print (responseSearch.json())
print ("\n")

responseDelete = requests.delete(url=postUri)
print("delete profile:\n")
print("------------\n")
print (responseDelete)
print ("\n")
