import os, requests
from dotenv import load_dotenv
load_dotenv()

URL = "https://api.yapper.website/rest/v1/rpc/who_online"

APIKEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuZmt1cXpkZHd2dGRvanpnbWRtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTE2Mzk0ODgsImV4cCI6MjEwNzIxNTQ4OH0.kMZcUf8DgMrYFNGtMPW9SGja2m1cRdMq5WJv5XBNgCU"

HEADERS = {
    "accept": "*/*",
    "apikey": APIKEY,
    "Authorization": f"Bearer {os.environ.get("USER_API_KEY")}",
    "content-profile": "public",
    "content-type": "application/json",
    "x-client-info": "supabase-js/2.117.3; runtime=web",
    "origin": "https://www.yapin.gg",
    "referer": "https://www.yapin.gg/",
}

def who_online(server_id, extra=None, since=None):
    """
    Calls who_online with only the public anon apikey, no user session.
    Tells you whether the RPC is reachable/readable without authentication.
    """
    body = {"sid": server_id, "extra": list(extra or []), "since": since}
    r = requests.post(URL, headers=HEADERS, json=body, timeout=15)
    print(r.status_code)
    print(r.text)
    return r

if __name__ == "__main__":
    who_online("17c3e451-26ad-4443-9842-85b804e9519f")