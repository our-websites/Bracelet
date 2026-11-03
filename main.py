import yapper, os, sys
from pathlib import Path
from dotenv import load_dotenv
#from cloudflare import Cloudflare
from flask import Flask, render_template, jsonify, request, send_file, make_response, Response

load_dotenv()

MAIN_DIR = Path(__file__).parent
sys.path.insert(0, str(MAIN_DIR))

VARS = {}

envs = {
    "BASE_URL": True,
    "API_BASE_URL": False,
    "SERVER_PORT": True
}

missing_vars = []
for var in envs:
    var_data = str(os.environ.get(var, ""))
    print(var_data)
    if not var_data:
        missing_vars.append(var)
    else:
        VARS[var] = var_data.strip()
        print(f"[Bracelet] Sucessfully Added {var}!")

if len(missing_vars) >= 1:
    for variable in missing_vars:
        if envs[variable] == True:
            print(f"[Bracelet] MISSING VARIABLE: {variable} IN .env")
        else:
            print(f"[Bracelet] MISSING OPTIONAL VARIABLE: {variable} IN .env")
    sys.exit(1)

BASE_URL = VARS["BASE_URL"].strip()
BASE_URL_STRIPPED = BASE_URL.replace("http://", "")
BASE_URL_STRIPPED = BASE_URL_STRIPPED.replace("https://", "")
API_BASE_URL = VARS["API_BASE_URL"]
PORT = VARS["SERVER_PORT"]

app = Flask(__name__, subdomain_matching=True, template_folder=MAIN_DIR / "templates", static_folder=MAIN_DIR / "static")

app.config["SERVER_NAME"] = BASE_URL_STRIPPED

bot = yapper.Bot()

@bot.command("test", "Test Command Until We Actually Code This")
def test(interaction):
    interaction.reply("Test Worked!")

@app.route("/", methods=["GET"])
@app.route("/", methods=["GET", "HEAD"], subdomain="api")
def index():
    return jsonify({"data": "COMING SOON", "success": True})

@app.route("/<file>", methods=["GET"])
def serve_static(file):
    try:
        return send_file(f"{MAIN_DIR / 'static'}/{file}")
    except Exception:
        return "File Not Found", 404

app.run(host="0.0.0.0", port=PORT, debug=False)

bot.run()
