from hhub.plugins import LightsPlugin
import logging
from huepy import hue
from flask import Blueprint, request, render_template, g, current_app

PLUGIN_NAME = 'huepy'

admin = Blueprint(PLUGIN_NAME, __name__, template_folder="templates",
    static_folder='static')

@admin.route('/', methods=['GET', 'POST'])
def index():
    g.cfg = current_app.cfg
    g.settings = g.cfg.get(PLUGIN_NAME, {})
    if request.method == 'POST':
        g.settings['ip'] = request.form['ip']
        g.settings['username'] = request.form['username']
        g.cfg.save()
    return render_template('huepy/index.html')

@admin.route('/discover')
def discover():
    api = hue.Api()
    return api.discover()

def get_api():
    cfg = current_app.cfg
    settings = cfg.get(PLUGIN_NAME, {})
    api = hue.Api(settings.get('ip', None), settings.get('username', None))
    return api

@admin.route('/register')
def register():
    api = get_api()
    try:
        api.register()
    except Exception as e:
        return str(e), 500
    return '', 200

@admin.route('/test')
def test_connection():
    api = get_api()
    if api.test_connection():
        return '', 200
    return '', 500

class HuepyPlugin(LightsPlugin):
    plugin_id = PLUGIN_NAME
    admin = admin

    def __init__(self, *args, **kwargs):
        super(HuepyPlugin, self).__init__(*args, **kwargs)
        ip = self.config.get('ip', None)
        username = self.config.get('username', None)
        self.api = hue.Api(ip, username)

    def on_event(self, **kwargs):
        logging.info('HuepyPlugin event %s' % (kwargs))
        target_name = kwargs.pop('target', 'all')
        resource_id = kwargs.pop('id', None)

        target = getattr(self.api, target_name)

        if resource_id:
            target = target.find(resource_id)

        if kwargs.pop('off', False):
            # there's no off command, only on=False
            kwargs['on'] = False

        target.update(**kwargs)
