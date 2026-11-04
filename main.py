import yapper, os, sys
from pathlib import Path
from threading import Thread
from dotenv import load_dotenv
#from cloudflare import Cloudflare
from flask import Flask, render_template, jsonify, request, send_file, make_response, Response

load_dotenv()

global API_INFO

MAIN_DIR = Path(__file__).parent
sys.path.insert(0, str(MAIN_DIR))

API_INFO = {"Members": 0, "Servers": 0}

VARS = {}

envs = {
    "YAPPER_BOT_TOKEN": True,
    "BASE_URL": True,
    "API_BASE_URL": True,
    "INVITE_URL": True,
    "SERVER_PORT": True,
    "KV": False,
    "CLOUDFLARE_API_TOKEN": False, # Required if you enable KV support.
    "CLOUDFLARE_KV_NAMESPACE": False # Required if you enable KV support.
}

missing_vars = []
for var in envs:
    var_data = str(os.environ.get(var, ""))
    #print(var_data)
    if not var_data:
        missing_vars.append(var)
    else:
        VARS[var] = var_data.strip()
        print(f"[Bracelet] LOADED {var} INTO THE ENVIRONMENT!")

if len(missing_vars) >= 1:
    for variable in missing_vars:
        #print(missing_vars)
        if envs[variable] == True:
            print(f"[Bracelet] MISSING VARIABLE: {variable} IN .env")
        else:
            print(f"[Bracelet] MISSING OPTIONAL VARIABLE: {variable} IN .env")
        #print(missing_vars.index(variable))
    if len(missing_vars) >= 1 and envs[variable] == True:
        sys.exit(1)

BASE_URL = VARS["BASE_URL"].strip()
BASE_URL_STRIPPED = BASE_URL.replace("http://", "")
BASE_URL_STRIPPED = BASE_URL_STRIPPED.replace("https://", "")
API_BASE_URL = VARS["API_BASE_URL"]
INVITE_URL = VARS["INVITE_URL"]
PORT = VARS["SERVER_PORT"]

app = Flask(__name__, subdomain_matching=True, template_folder=MAIN_DIR / "templates", static_folder=MAIN_DIR / "static")

app.config["SERVER_NAME"] = BASE_URL_STRIPPED

bot = yapper.Bot()

@bot.on("ready")
def on_bot_start(bot_data):
    #print(bot_data)
    API_INFO["Members"] = SyncMembers()

@bot.on("member_join")
def Member_Join():
    API_INFO["Members"] = SyncMembers()

@bot.on("test")
def test_event():
    print(f"[Bracelet] Recieved Test Event! There Are Currently {API_INFO['Members']} Users Being Monitored.")

@bot.on("member_left")
def Member_Left():
    API_INFO["Members"] = SyncMembers()

def SyncServers():
    return bot.servers()

def SyncMembers():
    try:
        API_INFO["Servers"] = SyncServers()
    except Exception:
        return "Error Fetching Servers."
    if len(API_INFO["Servers"]) >= 1:
        count = 0
        for srv in API_INFO["Servers"]:
            #print(srv)
            srv_data = bot.member_counts(srv.get("id"))
            print(f"[Bracelet] {srv.get('name', 'Unknown Server')}: {srv_data.get('member_count', 0)} Members Monitored.")
            count += srv_data.get("member_count", 0)
        print(f"[Bracelet] Total Monitored User Count: {count}")
        return count
    else:
        return "No Servers Found? Maybe Yapin' Is Down Or You Configured Something Wrong, Or You Haven't Added Your Bot To A Server?"
    return "Failed To Sync Members."

@bot.command("test", "Test Command Until We Actually Code This")
def test(interaction):
    interaction.reply("Test Worked!")

@app.route("/", methods=["GET"])
@app.route("/", methods=["GET"], subdomain="api")
def index():
    API_RESPONSE = {"info": "Bracelet provides Yapin presences as an API. Find out more here: https://github.com/our-websites/bracelet","yapin_invite": VARS["INVITE_URL"],"monitored_user_count": API_INFO["Members"]}
    return jsonify({"data": API_RESPONSE, "success": True})

@app.route("/<file>", methods=["GET"])
def serve_static(file):
    try:
        return send_file(f"{MAIN_DIR / 'static'}/{file}")
    except Exception:
        return "File Not Found", 404

def start_bot():
    bot.run()

Thread(target=start_bot, daemon=True).start()

app.run(host="0.0.0.0", port=PORT, debug=True)
