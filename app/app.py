# secondrevision

from flask_api import FlaskAPI
import sys
import os

from flask_cors import CORS
from flask import Flask, request, abort, jsonify, send_from_directory

# from OpenSSL import SSL
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('rootCA.pem')

app = FlaskAPI(__name__)
CORS(app)
global running
global alreadydone
running = False
alreadydone = False

sys.path.insert(1, './scripts')


@app.route('/', methods=["GET"])
def api_root():
    return {
        "mom found the poop sock": "uh oh she found the pee drawer too"
    }


@app.route('/files', methods=["GET", "POST"])
def files():
    if request.method == "POST":

        print("posting")
        jsondata = request.data
        try:
            if jsondata["download"] == "True":
                print("getting")
                projdir = "./project/" + jsondata["name"]
                print("doodoo")
                return send_from_directory(projdir, "filetorun.py", as_attachment=True)
        except:
            print(jsondata)
            os.mkdir("./project/" + jsondata["name"])
            print("made dir")
            f = open("./project/" + jsondata["name"] + "/" + jsondata["name"] + ".py", "w")
            f.write(jsondata["content"])
            f.close()
            print("made filetorun")

            f = open("./project/" + jsondata["name"] + "/desc.txt", "w")
            f.write(jsondata["desc"])
            f.close()
            print("made desc")

            return {'create': "complete"}

    if request.method == "GET":
        print("getting")
        folders = os.listdir('project')
        a = {}

        for i in folders:
            # num = i[0]
            name = i
            filesin = os.listdir("./project/" + i)
            f = open("./project/" + i + "/desc.txt", "r")
            desciption = f.read()
            f.close()


            a.__setitem__(name, desciption)

        return a






if __name__ == "__main__":
    context = ('server.crt', 'server.key')
    app.run(ssl_context=context, threaded=False, debug=False)

# https://github.com/jasbur/RaspiWiFi
# that is link to wifi setup thing i use
# export FLASK_APP=fl-app.py
# sudo -E flask run --host=switch-hub.local --port=80 --cert=adhoc
# sudo -E flask run --host=switch-hub.local --port=80 --cert=server.crt --key=server.key

# export FLASK_APP=fl-app.py && sudo -E flask run --host=switch-hub.local --port=80 --cert=server.crt --key=server.key
