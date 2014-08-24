from hhub.plugins import LightsPlugin
import logging
from huepy import hue
from flask import Blueprint, render_template

admin = Blueprint('huepy', __name__, template_folder="templates",
    static_folder='static')

@admin.route('/')
def index():
    return render_template('huepy/index.html')

class HuepyPlugin(LightsPlugin):
    plugin_id = 'huepy'
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
