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
            raise Exception("Could not authenticate client.")

        data = r.json()
        now = datetime.datetime.now()
        accessToken = data["access_token"]
        expiresIn = data["expires_in"]
        expires = now + datetime.timedelta(seconds = expiresIn)
        self.accessToken = accessToken
        print(self.accessToken)
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
    
    def getTrack(self, _id):
        return self.getResource(_id, resourceType = "track")

    def base_search(self, queryParams):
        headers = self.getResourceHeader()
        endpoint = "https://api.spotify.com/v1/search"
        lookupURL = f"{endpoint}?{queryParams}"
        
        r = requests.get(lookupURL, headers = headers)
        print(r.status_code)
        if r.status_code not in range(200,299):
            return {}
        return r.json()
    
    def search(self, query = None, operator = None, operatorQuery = None, searchType = "artist"):
        if query == None:
            raise Exception("Query is required.")
        if isinstance(query, dict):            
            query = " ".join([f"{k}:{v}" for k,v in query.items()])
        if operator != None and operatorQuery != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operatorQuery, str):
                    query = f"{query} {operator} {operatorQuery}"
        queryParams = urlencode({"q" : query, "type" : searchType.lower()})
        return self.base_search(queryParams)

spotify = SpotifyAPI(clientID, clientSecret)
#print(spotify.search("track" : "Alone Again", "artist" : "Weeknd" searchType = "Track"))
#print(spotify.getArtist("1Xyo4u8uXC1ZmMpatF05PJ"))
#print(spotify.search(query = "Danger", operator = "Not", operatorQuery = "Zone", searchType = "track"))
print(spotify.getTrack("6tkjU4Umpo79wwkgPMV3nZ"))