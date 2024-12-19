from flask import Flask, render_template, jsonify, Response
from config import SECRET

import json

from datetime import datetime

from API.utils import DBAPIConnection

APIConn = DBAPIConnection(__file__)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.secret_key = SECRET

#region API ROUTES
@app.route('/API/lastsync', methods=['GET'])
def get_recent_sync_date():
    return jsonify(lastsync=APIConn.getLastDBSyncDate(iso=True)), 200
@app.route('/API/localtime', methods=['GET'])
def get_DB_local_time():
    return jsonify(localtime=datetime.now().isoformat()), 200

@app.route('/API/equipment', methods=['GET'])
def get_full_equip_list():
    r = APIConn.getDictedEquipData(ordering_args='rarity ASC, id ASC')
    resp = Response(json.dumps(r),  mimetype='application/json')
    resp.status_code = 200
    return resp
#endregion

#HOME ROUTE
@app.route('/')
def home():
    return render_template('index.html')

#EQUIP_ROOT ROUTE   
@app.route('/equipment')
def equip_root():
    return render_template('equip_root.html')

if __name__ == '__main__':
    app.run(debug=False)