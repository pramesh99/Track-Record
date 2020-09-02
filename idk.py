from flask import Flask, render_template, redirect, request, session, make_response,session,redirect, url_for
import spotipy
import spotipy.util as util
from startup import *
import time
import json
from urllib.parse import urlencode
import requests

app = Flask(__name__)

accessToken = ""
jsonResponse = {}

@app.route("/login")
def login():
    scope = "user-top-read"
    authParams = {"response_type": "code", "client_id": CLIENT_ID, "scope": scope, "redirect_uri": REDIRECT_URI}
    authURL = "https://accounts.spotify.com/authorize?" + urlencode(authParams)
    return redirect(authURL)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    tokenParams = {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    tokenURL = "https://accounts.spotify.com/api/token"
    tokenResponse = requests.post(url = tokenURL, data = tokenParams)

    if tokenResponse.status_code == 200:
        jsonResponse = tokenResponse.json()
        

        global accessToken
        accessToken = jsonResponse["access_token"]
        refreshToken = jsonResponse["refresh_token"]
        expiresIn = jsonResponse["expires_in"]

        return redirect(url_for("home"))
    return redirect(url_for("error"))
print(json.loads(jsonResponse))
def getTopTracks(timePeriod, limit, offset):
    endpoint = "https://api.spotify.com/v1/me/top/tracks"    
    queryParams = {"time_range": timePeriod, "limit": limit, "offset": offset}     
    lookupURL = endpoint + urlencode(queryParams)
    topTrackReply = requests.get(url = lookupURL, headers = {"Authorization": f"Bearer {accessToken}"}).json()
    return topTrackReply


def parseTopTracks():
    ranges = ['short_term', 'medium_term', 'long_term']
    info = []
    for sp_range in ranges:
        info.append("Range: {}".format(sp_range))
        results = getTopTracks(sp_range, 10, 0)
        for i, item in enumerate(results['items']):
            info.append("{}: {} by {}".format(i + 1, item["name"], item['artists'][0]['name']))
        info.append("")
    return info
    
@app.route("/home")
def home():
    return f"{accessToken}" #render_template("index.html", info = getTopTracks("medium_term", 10, 0))

if __name__ == "__main__":
    app.run(debug=True)

