# coding: utf-8
from pianette.utils import Debug
from pianette.PianetteCmd import PianetteCmdUtil
from flask import Flask, render_template, request, send_from_directory
from threading import Thread

app = Flask(__name__, template_folder='../templates', static_folder='../templates')

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Static routes for images
@app.route('/<directory>/<path:path>')
def send_static(directory, path):
    if directory in ['images', 'js', 'css']:
        return send_from_directory(directory, path)
    else:
        return ('', 404)

@app.route('/favicon.ico')
def send_favicon():
    return send_from_directory('favicons', 'favicon.ico')

@app.route('/', methods = ['GET'])
def home():
    return render_template('index.html', url_root=request.url_root)

@app.route('/admin', methods = ['GET'])
def admin():
    # Let's list available configs
    return render_template('admin.html', url_root=request.url_root, configs=app.configs, current_config=app.pianette.get_selected_game())

# The main endpoint for issuing a command for Pianette
@app.route('/<namespace>/<command>', methods = ['POST'])
def console_play(namespace, command):
    if PianetteCmdUtil.is_supported_cmd_namespace(namespace):
        full_command = "%s.%s %s" % (namespace, command, request.form.get('data'))
        app.pianette.inputcmds(full_command, source="api")
        return ('1', 200)
    else:
        return ('0', 404)

@app.route('/', methods = ['POST'])
def raw_command():
    app.pianette.inputcmds(request.form.get('data'), source="api")
    return ('1', 200)


class PianetteApi:

    def __init__(self, configobj=None, pianette=None, **kwargs):
        super().__init__(**kwargs)
        app.pianette = pianette
        app.configs = configobj.get("Game").keys()

        Debug.println("INFO", "Starting API thread")
        t = Thread(target=self.startApi)
        t.daemon = True
        t.start()

    def startApi(self):
        app.run(debug=False, threaded=True, host="0.0.0.0")
