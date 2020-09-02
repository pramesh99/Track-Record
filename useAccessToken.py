import base64
import requests
import datetime
from urllib.parse import urlencode

clientID = "8ca7b0fc46c54a0e895d9b1115fc9cfb"
clientSecret = "080f0e59008c471a94c17619d25af8f9"


class SpotifyAPI(object):
    accessToken = None
    accessTokenExpires = datetime.datetime.now()
    accessTokenDidExpire = True
    clientID = None
    clientSecret = None
    tokenURL = "https://accounts.spotify.com/api/token"

    def __init__(self, clientID, clientSecret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clientID = clientID
        self.clientSecret = clientSecret

    def getClientCredentials(self):
        #returns b64 encoded string
        clientID = self.clientID
        clientSecret = self.clientSecret
        if clientSecret == None or clientID == None:
            raise Exception("Set clientID and clientSecret")
        clientCreds = f"{clientID}:{clientSecret}"
        b64clientCreds = base64.b64encode(clientCreds.encode()) # encode turns str into bytes
        return b64clientCreds.decode()

    def getTokenHeader(self):
        b64clientCreds = self.getClientCredentials()
        return {"Authorization" : f"Basic {b64clientCreds}"}

    def getTokenData(self):
        return {"grant_type" : "client_credentials"}

    def performAuth(self):
        tokenURL = self.tokenURL
        tokenData = self.getTokenData()
        tokenHeader = self.getTokenHeader()
        r = requests.post(tokenURL, data = tokenData, headers = tokenHeader)
        if r.status_code not in range(200,299):
            return False

        data = r.json()
        now = datetime.datetime.now()
        accessToken = data["access_token"]
        expiresIn = data["expires_in"]
        expires = now + datetime.timedelta(seconds = expiresIn)
        self.accessToken = accessToken
        self.accessTokenExpires = expires
        self.accessTokenDidExpire = expires < now
        return True

spotify = SpotifyAPI(clientID, clientSecret)
spotify.performAuth()

accessToken = spotify.accessToken

headers = {"Authorization" : f"Bearer {accessToken}"}

topType = "artists" # or "tracks"
endpoint = f"https://api.spotify.com/v1/me/top/{topType}"
data = urlencode({"q" : "Time", "type" : "track"})
print(data)
lookupURL = f"{endpoint}"

r = requests.get(lookupURL, headers = headers)
print(r.status_code)
print(r.json())


# data = urlencode({"q" : "Prisoner", "type" : "track"})
# lookupURL = f"{endpoint}?{data}"
# r = requests.get(lookupURL, headers = headers)
# print(r.json())


# clientCreds = f"{clientID}:{clientSecret}"
# b64clientCreds = base64.b64encode(clientCreds.encode()) # encode turns str into bytes

# tokenURL = "https://accounts.spotify.com/api/token"
# method = "POST" # look up

# tokenData = { "grant_type" : "client_credentials"}
# tokenHeader = {"Authorization" : f"Basic {b64clientCreds.decode()}"}

# def performAuth(b64clientCreds):
#     r = requests.post(tokenURL, data = tokenData, headers = tokenHeader)
#     if r.status_code not in range(200,299):
#             return False
#     data = r.json()
#     now = datetime.datetime.now()
#     accessToken = data["access_token"]
#     expiresIn = data["expires_in"]
#     expires = now + datetime.timedelta(seconds = expiresIn)
#     return accessToken

# token = performAuth(b64clientCreds)
# headers = {"Authorization" : f"Bearer {token}"}
# print(token)

# topType = "artists" # or "tracks"
# endpoint = f"https://api.spotify.com/v1/me/top/{topType}"
# print(endpoint)

# timePeriod = "long_term" # or "short_term" or "medium_term" for last month and last 6 months respectively4
# queryParams = urlencode({"time_range" : timePeriod})
# print(queryParams)

# lookupURL = f"{endpoint}"
# print(lookupURL)

# r = requests.get(lookupURL, headers = headers)
# print(r.status_code)