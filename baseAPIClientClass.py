import base64
import requests
import datetime

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
        print(r.status_code)
        if r.status_code not in range(200,299):
            return False

        data = r.json()
        now = datetime.datetime.now()
        accessToken = data["access_token"]
        expiresIn = data["expires_in"]
        expires = now + datetime.timedelta(seconds = expiresIn)
        self.accessTokenExpires = expires
        self.accessTokenDidExpire = expires < now
        return True


client = SpotifyAPI(clientID, clientSecret)
print(client.performAuth())



