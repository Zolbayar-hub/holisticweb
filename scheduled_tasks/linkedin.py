from flask import Flask, request, redirect
import requests
import urllib.parse
import webbrowser
import json
import os

app = Flask(__name__)

CLIENT_ID = "86her6i30qcny2"
CLIENT_SECRET = "WPL_AP1.nDxnjy6QulanzaWl.+h8PBg=="
REDIRECT_URI = "http://localhost:5000/callback"  # Must match app settings
SCOPES = "w_member_social"
TOKEN_FILE = "linkedin_tokens.json"

def save_tokens(data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return {}

def refresh_access_token(refresh_token):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    tokens = response.json()
    if "access_token" in tokens:
        tokens["refresh_token"] = tokens.get("refresh_token", refresh_token)
        save_tokens(tokens)
    return tokens

def post_to_linkedin(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get("https://api.linkedin.com/v2/me", headers=headers).json()
    person_urn = profile_response.get("id")
    if not person_urn:
        return {"error": "Could not fetch user profile"}

    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers["Content-Type"] = "application/json"
    payload = {
        "author": f"urn:li:person:{person_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": "Hello World from Flask! 🚀"},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    return requests.post(post_url, headers=headers, json=payload).json()

@app.route("/")
def index():
    tokens = load_tokens()

    # If refresh token exists → refresh and post
    if "refresh_token" in tokens:
        tokens = refresh_access_token(tokens["refresh_token"])
        if "access_token" in tokens:
            result = post_to_linkedin(tokens["access_token"])
            return f"✅ Post Result: {result}"
        return f"❌ Failed to refresh token: {tokens}"

    # If only access token exists (no refresh) → post until it expires
    if "access_token" in tokens:
        result = post_to_linkedin(tokens["access_token"])
        return f"✅ Post Result: {result}"

    # No tokens → trigger OAuth login
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={urllib.parse.quote(SCOPES)}"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No authorization code received. Please try again."

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    tokens = response.json()

    if "access_token" in tokens:
        save_tokens(tokens)
        return "✅ Tokens saved! Re-run script to post automatically."
    else:
        return f"❌ Error: {tokens}"

if __name__ == "__main__":
    webbrowser.open("http://localhost:5000/")
    app.run(port=5000)
