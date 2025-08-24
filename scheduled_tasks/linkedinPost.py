from flask import Flask, request, redirect
import requests
import urllib.parse
import webbrowser

app = Flask(__name__)


CLIENT_ID = "86her6i30qcny2"
CLIENT_SECRET = "WPL_AP1.nDxnjy6QulanzaWl.+h8PBg=="
REDIRECT_URI = "http://localhost:5000/callback"  # Must match app settings
SCOPES = "w_member_social"

# Step 1: Start OAuth flow
@app.route("/")
def index():
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={urllib.parse.quote(SCOPES)}"
    )
    return redirect(auth_url)

# Step 2: Handle LinkedIn redirect
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No authorization code received. Please try again."

    # Exchange code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    token_info = response.json()

    if "access_token" in token_info:
        return f"Access Token: {token_info['access_token']}"
    else:
        return f"Error: {token_info}"

if __name__ == "__main__":
    webbrowser.open("http://localhost:5000/")
    app.run(port=5000)
