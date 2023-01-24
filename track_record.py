from flask import Flask, render_template, redirect, request, make_response,session,redirect, url_for
import spotipy
import spotipy.util as util
from secretStuff import *
import requests
from urllib.parse import urlencode
import datetime
import json

app = Flask(__name__)
accessToken = None
expiresIn = None
expires = None

#app.secret_key = SECRET_KEY
baseURL = "https://accounts.spotify.com"

@app.route("/")
def landingPage():
    return render_template("landingPage.html")

# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
@app.route("/login")
def verify():
    authParams = {"response_type": "code","client_id": CLIENT_ID, "scope": SCOPE, "redirect_uri": REDIRECT_URI}
    authURL = f"{baseURL}/authorize?{urlencode(authParams)}" # the ? is important!
    return redirect(authURL)

# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/callback")
def api_callback():    
    code = request.args.get('code')
    authTokenURL = f"{baseURL}/api/token"
    tokenParams = {
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":REDIRECT_URI,
        "client_id":CLIENT_ID,
        "client_secret":CLIENT_SECRET
        }
    tokenResponse = requests.post(url = authTokenURL, data = tokenParams)
    
    if tokenResponse.status_code in range(200,299):
        tokenResponsejson = tokenResponse.json()

        global accessToken
        global expiresIn
        global expires
        accessToken = tokenResponsejson["access_token"]
        refreshToken = tokenResponsejson["refresh_token"]
        now = datetime.datetime.now()
        expiresIn = tokenResponsejson["expires_in"]
        expires = now + datetime.timedelta(seconds = expiresIn)
        print(expires)
        return redirect(url_for("artists"))
    
    return redirect(url_for("error"))
   

@app.route("/error")
def error():
    return "<h1>ERROR</h1>"

def checkTokenValidity():
    global expires
    now = datetime.datetime.now()
    if expires < now:
        return redirect(url_for("verify"))
    return accessToken

@app.route("/TopArtists")
def artists():
    return render_template("topArtists.html", info = getTopArtists()[0], info2 = getTopArtists()[1], info3 = getTopArtists()[2])

@app.route("/TopTracks")
def tracks():
    return render_template("topTracks.html", info = getTopTracks()[0], info2 = getTopTracks()[1], info3 = getTopTracks()[2])

@app.route("/test")
def test():
    return render_template("results.html", info = getTopTracks()[0])

def getTopTracks():   
    spotify = spotipy.Spotify(auth=accessToken)

    info = []
    results = user = spotify.current_user_top_tracks(time_range = "short_term", limit = 50)
    
    for i, item in enumerate(results['items']):
        info.append("{}: {} by {}".format(i + 1, item["name"], item['artists'][0]['name']))
    info.append("\n")

    info2 = []    
    results = user = spotify.current_user_top_tracks(time_range = "medium_term", limit = 50)
    for i, item in enumerate(results['items']):
        info2.append("{}: {} by {}".format(i + 1, item["name"], item['artists'][0]['name']))
    info2.append("\n")

    info3 = []    
    results = user = spotify.current_user_top_tracks(time_range = "long_term", limit = 50)
    for i, item in enumerate(results['items']):
        info3.append("{}: {} by {}".format(i + 1, item["name"], item['artists'][0]['name']))
    info3.append("\n")
    print(type(info))

    return info, info2, info3



def getTopArtists():
    spotify = spotipy.Spotify(auth=checkTokenValidity())

    info = []        
    results = spotify.current_user_top_artists(time_range = "short_term", limit = 50)

    for i, item in enumerate(results["items"]):
        info.append("{}. {}".format(i + 1, item['name']))
    info.append("\n")

    info2 = []        
    results = spotify.current_user_top_artists(time_range = "medium_term", limit = 50)
    for i, item in enumerate(results["items"]):
        info2.append("{}. {}".format(i + 1, item['name']))
    info2.append("\n")

    info3 = []        
    results = spotify.current_user_top_artists(time_range = "long_term", limit = 50)
    for i, item in enumerate(results["items"]):
        info3.append("{}. {}".format(i + 1, item['name']))
    info3.append("\n")

    return info, info2, info3


# authorization-code-flow Step 3.
# Use the access token to access the Spotify Web API;
# Spotify returns requested data
@app.route("/go", methods=['POST'])
def go():
    data = request.form    
    sp = spotipy.Spotify(auth=session['toke'])
    response = sp.current_user_top_artists(limit=data['num_tracks'], time_range=data['time_range'])
    return render_template("results.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
