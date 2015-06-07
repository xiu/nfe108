from flask import Flask, session, render_template, request, Response, abort, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship
import json
import xmlrpc.client

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)

LOGIN="admin"
PASSWORD="admin"

# Make authentication mandatory
def check_auth(username, password):
    if username == LOGIN and password == PASSWORD:
        return True
    return False

def authenticate():
    """ sends a 401 response that enable basic auth """
    resp = Response(json.dumps({"error": "session expired"}))
    resp.status_code=401
    h = resp.headers
    h['Access-Control-Allow-Origin'] = request.headers["Origin"] if "Origin" in request.headers else None
    h['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
    h['Access-Control-Max-Age'] = str(21600)
    h['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, *'
    return resp

@app.before_request
def requires_auth(*args, **kwargs):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

# models
class Pool(db.Model):
    __tablename__ = "pool"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    app_web = db.Column(db.String(250))
    app_loading = db.Column(db.String(250))
    servers = relationship('Server', backref='pool', lazy="dynamic")

    def __init__(self, name, app_web, app_loading):
        self.name = name
        self.app_web = app_web
        self.app_loading = app_loading

    def set_version(self, name, version):
        if name == "app_web":
            self.app_web = version
        elif name == "app_loading":
            self.app_loading = version
        db.session.add(self)
        db.session.commit()

    def get_version(self, name, version):
        if name == "app_web":
            return self.app_web
        elif name == "app_loading":
            return self.app_loading

class Server(db.Model):
    __tablename__ = "server"
    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey('pool.id'))
    host = db.Column(db.String(250))

    def __init__(self, pool_id, host):
        self.pool_id = pool_id
        self.host = host

    def list_services(self):
        server = xmlrpclib.Server('http://' + self.host + ':9001/RPC2')
        server.supervisor.getAllProcessInfo()

    def stop(self, name):
        server = xmlrpc.client.Server('http://' + self.host + ':9001/RPC2')
        server.supervisor.stopProcess(name, wait=True)

    def start(self, name):
        server = xmlrpc.client.Server('http://' + self.host + ':9001/RPC2')
        server.supervisor.startProcess(name, wait=True)

    def restart(self, name):
        self.stop(name)
        self.start(name)

    def get_enc(self):
        obj = {"classes": {"app_web": self.pool.app_web, "app_loading": self.pool.app_loading}}
        return obj
        

# API
@app.route("/pool", methods=['GET'])
@app.route("/pool/<string:pool_name>", methods=['GET'])
def pool(pool_name=None):
    if pool_name:
        try:
            pool = Pool.query.filter_by(name=pool_name).one()
        except NoResultFound:
            abort(404)

        serverlist=[]
        for server in pool.servers:
            serverlist.append(server.host)

        return jsonify({"pool": {"name": pool.name, "servers": serverlist, "app_web": pool.app_web, "app_loading": pool.app_loading}})
    else:
        pool = Pool.query.all()
        
        obj = {'pools': []}
        for p in pool:
            obj['pools'].append(p.name)

        return jsonify(obj)

@app.route("/pool/<string:pool_name>", methods=['PUT'])
def pool_update(pool_name):
    try:
        pool = Pool.query.filter_by(name=pool_name).one()
    except NoResultFound:
        abort(404)

    data = request.json

    try:
        pool.set_version("app_loading", data["app_loading"])
    except KeyError:
        pass

    try:
        pool.set_version("app_web", data["app_web"])
    except KeyError:
        pass

    return jsonify({"pool": {"name": pool.name, "app_web": pool.app_web, "app_loading": pool.app_loading}})

@app.route("/server", methods=['GET'])
@app.route("/server/<string:server_host>", methods=['GET'])
def server(server_host=None):
    if server_host:
        server = Pool.query.filter_by(host=server_host).one()
        
        return {"server": {"pool": server.pool.name, "host": server.host}}
    else:
        servers = Server.query.all()

        obj = {"servers": []}
        for s in servers:
            obj['servers'].append(s)

        return jsonify(obj)


if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0")


