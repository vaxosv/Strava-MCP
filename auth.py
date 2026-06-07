import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import set_key

CLIENT_ID = "213881"
CLIENT_SECRET = "4b24ec9ec6c5146e859cbc6103010207b9571551"
REDIRECT_URI = "http://localhost:8080"
SCOPE = "read,activity:read_all"
ENV_PATH = ".env"

auth_url = (
    f"https://www.strava.com/oauth/authorize"
    f"?client_id={CLIENT_ID}&response_type=code"
    f"&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope={SCOPE}"
)

code = None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global code
        qs = parse_qs(urlparse(self.path).query)
        code = qs.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if code:
            self.wfile.write(b"<h1>Authorized! You can close this tab.</h1>")
        else:
            self.wfile.write(b"<h1>No code found. Try again.</h1>")
        self.server.shutdown()

    def log_message(self, *a):
        pass


print("1. Opening browser for Strava authorization...")
import webbrowser
webbrowser.open(auth_url)

print("2. Waiting for redirect on http://localhost:8080 ...")
server = HTTPServer(("localhost", 8080), Handler)
server.serve_forever()

if not code:
    print("Failed to get authorization code.")
    exit(1)

print(f"3. Exchanging code for tokens...")
resp = requests.post("https://www.strava.com/oauth/token", data={
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "authorization_code",
    "code": code,
})
data = resp.json()

access = data["access_token"]
refresh = data["refresh_token"]
scope = data["scope"]

print(f"   Scope: {scope}")
print(f"   Access: {access[:20]}...")
print(f"   Refresh: {refresh[:20]}...")

set_key(ENV_PATH, "STRAVA_ACCESS_TOKEN", access)
set_key(ENV_PATH, "STRAVA_REFRESH_TOKEN", refresh)
print(f"4. Tokens saved to {ENV_PATH}!")