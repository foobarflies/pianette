# coding: utf-8
from pianette.utils import Debug
from flask import Flask, render_template, request
from threading import Thread

app = Flask(__name__, template_folder='../templates')

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/', methods = ['GET'])
def home():
    return render_template('index.html', url_root=request.url_root)

@app.route('/console/play', methods = ['POST'])
def console_play():
    command = "console.play %s" % (request.form.get('command'))
    app.pianette.inputcmds(command, source="api")
    return ('1', 200)

class PianetteApi:

    def __init__(self, configobj=None, pianette=None, **kwargs):
        super().__init__(**kwargs)
        self.configobj = configobj
        app.pianette = pianette

        Debug.println("INFO", "Starting API thread")
        t = Thread(target=self.startApi)
        t.daemon = True
        t.start()

    def startApi(self):
        app.run(debug=False, threaded=True, host="0.0.0.0")
