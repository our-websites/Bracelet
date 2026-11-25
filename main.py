import yapper, os, sys, time
from pathlib import Path
from threading import Thread
from dotenv import load_dotenv
from yapper import telemetry
from flask import Flask, render_template, jsonify, request, send_file, redirect

load_dotenv()

class BraceletData:
    status = "offline",
    user = {},
    kv = {}

    def __init__(self, status, user, kv):
        self.status = status
        self.user = user
        self.kv = kv

global API_INFO

MAIN_DIR = Path(__file__).parent
sys.path.insert(0, str(MAIN_DIR))

API_INFO = {"Members": 0, "Servers": {}}

VARS = {}

envs = {
    "YAPPER_BOT_TOKEN": True,
    "APPROVED_SERVERS": True, # These are comma separated servers that Bracelet is allowed to monitor users on.
    "BASE_URL": True,
    "API_BASE_URL": True,
    "INVITE_URL": True,
    "SERVER_PORT": True,
    "KV": True,
    "CLOUDFLARE_API_TOKEN": False, # Required if you enable KV support.
    "CLOUDFLARE_KV_NAMESPACE": False, # Required if you enable KV support.
    "TELEMETRY_KEY": False
}

missing_vars = []
for var in envs:
    var_data = str(os.environ.get(var, ""))
    if not var_data:
        missing_vars.append(var)
    else:
        VARS[var] = var_data.strip()
        print(f"[Bracelet] LOADED {var} INTO THE ENVIRONMENT!")

if len(missing_vars) >= 1:
    for variable in missing_vars:
        if envs[variable] == True:
            print(f"[Bracelet] MISSING VARIABLE: {variable} IN .env")
        else:
            print(f"[Bracelet] MISSING OPTIONAL VARIABLE: {variable} IN .env")
    if len(missing_vars) >= 1 and envs[variable] == True:
        sys.exit(1)

BASE_URL = VARS["BASE_URL"].strip()
BASE_URL_STRIPPED = BASE_URL.replace("http://", "")
BASE_URL_STRIPPED = BASE_URL_STRIPPED.replace("https://", "")
API_BASE_URL = VARS["API_BASE_URL"]
INVITE_URL = VARS["INVITE_URL"]
PORT = VARS["SERVER_PORT"]
APPROVED_SERVERS = {str(id) for id in VARS["APPROVED_SERVERS"].split(',')}
KV = VARS["KV"]

global kv_database

if KV == (True or "true"):
    from cloudflare import Cloudflare
    kv_client = Cloudflare(api_token=os.environ.get("CLOUDFLARE_API_TOKEN")) # No clue if we'll use D1 or KV from Cloudflare.

app = Flask(__name__, subdomain_matching=True, template_folder=MAIN_DIR / "templates", static_folder=MAIN_DIR / "static")

app.config["SERVER_NAME"] = BASE_URL_STRIPPED

bot = yapper.Bot()
#print(telemetry.preview(bot))
telemetry.enable(bot, interval=300)

@bot.on("ready")
def on_bot_start(bot_data):
    bot.is_ready = True
    API_INFO["Members"] = SyncMembers()

@bot.on("member_join")
def Member_Join():
    API_INFO["Members"] = SyncMembers()

@bot.on("test")
def test_event():
    API_INFO["Members"] = SyncMembers()
    print(f"[Bracelet] Recieved Test Event! There Are Currently {API_INFO['Members']} User(s) Being Monitored.")

@bot.on("member_leave")
def Member_Left():
    API_INFO["Members"] = SyncMembers()

def bracelet_data(UserID=None, Username=None):
    print(UserID, Username)
    if not (UserID or Username): info = {"data": 'No UserID or Username Provided.', "success": False}
    if Username:
        info = {"data": f'Not Implemented Yet ({Username})', "success": False}
    elif UserID:
        info = pretty_format({"status": "offline" ,"user": bot.user(UserID), "kv": {}})
        #return jsonify({"data": f'Not Implemented Yet ({UserID})', "success": False})
    else:
        info = {"data": "No Data Found Or Provided.", "success": False}
    return info

def bracelet_kv(UID):
    return {}

def pretty_format(data: BraceletData):
    # (optional) Check if the user has KV data and add it to the table if there is KV data set.
    data['user']['kv'] = bracelet_kv(data['user']['id']) if KV == True else {}
    for badge in data['user']['badges']:
        if badge == ('bot' or 'verified_bot'):
            data['user']['object'] = 'bot'
    data['user']['avatar_url'] = f"https://files.yapper.website/avatars/{data['user']['avatar_path']}"
    data['user']['banner_url'] = f"https://files.yapper.website/banners/{data['user']['banner_path']}"
    # Format the data into a simple JSON response.
    formatted_data = {"data": data, "success": True}
    # Remove the avatar path and banner path keys from the JSON response as we give the full url paths.
    del formatted_data['data']['user']['avatar_path']
    del formatted_data['data']['user']['banner_path']
    # Return the formatted JSON data to bracelet_data() so it can return it back to the API or the command that triggered it.
    return formatted_data

def SyncServers():
    servers = []
    Servers = []
    for server in bot.servers():
        for APPROVED_SERVER in APPROVED_SERVERS:
            if APPROVED_SERVER == str(server['id']):
                servers.append(server)
            else:
                Servers.append(server)
    for srv in Servers:
        for asrv in servers:
            if str(asrv['id']) == str(srv['id']):
                Servers.pop(Servers.index(srv))
    print(f"There are {len(Servers)} Server(s) that aren't approved.")
    return servers

def SyncMembers():
    try:
        API_INFO["Servers"] = SyncServers()
    except Exception as e:
        return f"Error Fetching Servers: {e}"
    if bot.is_ready == True:
        count = 0
        for srv in API_INFO["Servers"]:
            srv_data = bot.member_counts(srv.get('id'))
            print(f"[Bracelet] {srv.get('name', 'Unknown Server')}: {srv_data.get('member_count', 0)} User(s) Monitored.")
            count += srv_data.get("member_count", 0)
        print(f"[Bracelet] Total Monitored User Count: {count}")
        return count
    else:
        print("[Bracelet] No Servers Found? Maybe Yapin' Is Down Or You Configured Something Wrong, Or You Haven't Set An Approved Server?")
        return "No Servers Found? Maybe Yapin' Is Down Or You Configured Something Wrong, Or You Haven't Set An Approved Server?"
    return "Failed To Sync Members."

@bot.command("test", "Test Command Until We Actually Code This")
def test(msg):
    msg.ephemeral("Test Worked!")

@bot.command("bracelet", "Get The Bracelet Info Of A User", options=[{"name": "user", "type": "user", "value": "self", "required": True}])
def bracelet_command(msg):
    print(msg.options)
    if msg.options['user'] == "self":
        msg.options['user'] = msg.author_id
    data = bracelet_data(UserID=msg.options['user'])
    data = data['data'] # We don't need to pass in the WHOLE JSON table, I will eventually make this an embed dw. (If I ever learn how to make a nice looking embed.) Feel free to open a PR adding a embed.
    msg.reply(data)

@bot.command("set", "Coming Soon!")
def set_kv(msg):
    msg.ephemeral("W.I.P")

@bot.command("get", "Coming Soon!")
def get_kv(msg):
    msg.ephemeral("W.I.P")

@bot.command("apikey", "Coming Soon!")
def generate_key(msg):
    msg.ephemeral("W.I.P")

@app.route("/<subdomains>", methods=["GET"], subdomain="<subdomain>")
@app.route("/", methods=["GET"], subdomain="<subdomain>")
@app.errorhandler(404)
def not_found(subdomain):
    if subdomain == "api":
        return redirect(API_BASE_URL)
    else:
        return redirect(BASE_URL) # Redirect to the main landing page as they're not on the API at all

@app.route("/", methods=["GET", "HEAD"])
def index():
    if API_BASE_URL == BASE_URL:
        return api_index()
    else:
        return redirect(API_BASE_URL) # Will be making a landing page at some point, for now it's just a redirect!

@app.route("/", methods=["GET", "HEAD"], subdomain="api")
def api_index():
    API_RESPONSE = {"info": "Bracelet provides Yapin presences as an API. Find out more here: https://github.com/our-websites/bracelet","yapin_invite": VARS["INVITE_URL"],"monitored_user_count": API_INFO["Members"]}
    return jsonify({"data": API_RESPONSE, "success": True})



@app.route("/api/v1/users/<UserID>", methods=["GET"]) # For local testing + people who don't want to use subdomains or don't have access to use subdomains.
@app.route("/v1/users/<UserID>", methods=["GET"], subdomain="api")
def bracelet_api(UserID):
    #print(bot.me)
    data = {"data": "An Error Occurred If You See This, or Bracelet isn't configured properly. Consider checking that you have a approved server set in your environment/.env!", "success": False}
    MemberData = None
    for server in API_INFO['Servers']:
        ServerMembers = bot.members(server.get('id'))
        for member in ServerMembers:
            if str(member['id']) == str(UserID):
                MemberData = bracelet_data(UserID=UserID)
    if not MemberData and len(API_INFO['Servers']) >= 1:
        data = {"data": "User is not monitored by Bracelet", "success": False}
    elif MemberData and len(API_INFO['Servers']) >= 1:
        data = MemberData
    else:
        pass
    return jsonify(data)

@app.route("/<file>", methods=["GET"])
def serve_static(file):
    try:
        return send_file(f"{MAIN_DIR / 'static'}/{file}")
    except Exception:
        return "File Not Found", 404

def start_bot():
    bot.run()

def syncer():
    try:
        while True:
            time.sleep(60) # Sync every minute.
            API_INFO["Members"] = SyncMembers()
            #print(f"[Bracelet] {len(API_INFO['Servers'])} Server(s) and {API_INFO['Members']} Member(s) Synced Successfully!")
    except KeyboardInterrupt:
        pass

Thread(target=syncer, daemon=True).start()
Thread(target=start_bot, daemon=True).start()
app.run(host="0.0.0.0", port=PORT, debug=False)
