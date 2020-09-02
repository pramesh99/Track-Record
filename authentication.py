import base64
import requests
import datetime

clientID = "8ca7b0fc46c54a0e895d9b1115fc9cfb"
clientSecret = "c1555d80d1b643bd86476b8fb394bd05"

clientCreds = f"{clientID}:{clientSecret}"
b64clientCreds = base64.b64encode(clientCreds.encode()) # encode turns str into bytes

tokenURL = "https://accounts.spotify.com/api/token"
method = "POST" # look up

tokenData = { "grant_type" : "client_credentials"}
tokenHeader = {"Authorization" : f"Basic {b64clientCreds.decode()}"}

r = requests.post(tokenURL, data = tokenData, headers = tokenHeader)
validRequest = r.status_code in range(200,299)

if validRequest:
    tokenResponseData = r.json()
    now = datetime.datetime.now()
    accessToken = tokenResponseData["access_token"]
    expiresIn = tokenResponseData["expires_in"]
    expires = now + datetime.timedelta(seconds=expiresIn)
    didExpire = expires < now

print(r.json())
