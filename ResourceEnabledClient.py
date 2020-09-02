import base64
import requests
import datetime
from urllib.parse import urlencode

clientID = "8ca7b0fc46c54a0e895d9b1115fc9cfb"
clientSecret = "c1555d80d1b643bd86476b8fb394bd05"


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
            raise Exception("Could not authenticate client.")

        data = r.json()
        now = datetime.datetime.now()
        accessToken = data["access_token"]
        expiresIn = data["expires_in"]
        expires = now + datetime.timedelta(seconds = expiresIn)
        self.accessToken = accessToken
        self.accessTokenExpires = expires
        self.accessTokenDidExpire = expires < now
        return True
    
    def getAccessToken(self):
        token = self.accessToken
        expires = self.accessTokenExpires
        now = datetime.datetime.now()
        if expires < now or token == None:
            self.performAuth()
            return self.getAccessToken()

        return token
    
    def getResourceHeader(self):
        accessToken = self.getAccessToken()
        headers = {"Authorization" : f"Bearer {accessToken}"}
        return headers

    def getResource(self, lookupID, resourceType = "albums", version = "v1"):
        endpoint = f"https://api.spotify.com/{version}/{resourceType}/{lookupID}"
        headers = self.getResourceHeader()
        r = requests.get(endpoint, headers = headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def getAlbum(self, _id):
        return self.getResource(_id, resourceType = "albums")

    def getArtist(self, _id):
        return self.getResource(_id, resourceType = "artists")

    def search(self, query, searchType = "artist"):
        headers = self.getResourceHeader()
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q" : query, "type" : searchType.lower()})
        lookupURL = f"{endpoint}?{data}"
        r = requests.get(lookupURL, headers = headers)
        print(r.status_code)
        if r.status_code not in range(200,299):
            return {}
        return r.json()


spotify = SpotifyAPI(clientID, clientSecret)
#print(spotify.search("Alone Again", searchType = "Track"))
print(spotify.getArtist("1Xyo4u8uXC1ZmMpatF05PJ"))