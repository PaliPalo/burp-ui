# -*- coding: utf8 -*-
"""
Burp-UI is a web-ui for burp backup written in python with Flask and
jQuery/Bootstrap

.. module:: burpui
    :platform: Unix
    :synopsis: Burp-UI main module.

.. moduleauthor:: Ziirish <ziirish@ziirish.info>
"""

import os
import sys
import logging

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf-8')

__title__ = 'burp-ui'
__author__ = 'Benjamin SANS (Ziirish)'
__author_email__ = 'ziirish+burpui@ziirish.info'
__url__ = 'https://git.ziirish.me/ziirish/burp-ui'
__description__ = 'Burp-UI is a web-ui for burp backup written in python with Flask and jQuery/Bootstrap'
__license__ = 'BSD 3-clause'
__version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'VERSION')).read().rstrip()
try:
    __release__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'RELEASE')).read().rstrip()
except:
    __release__ = 'unknown'

bui = None


def lookup_config(conf=None):
    ret = None
    if conf:
        if os.path.isfile(conf):
            ret = conf
        else:
            raise IOError('File not found: \'{0}\''.format(conf))
    else:
        root = os.path.join(
            sys.prefix,
            'share',
            'burpui',
            'etc'
        )
        conf_files = [
            '/etc/burp/burpui.cfg',
            os.path.join(root, 'burpui.cfg'),
            os.path.join(root, 'burpui.sample.cfg')
        ]
        for p in conf_files:
            if os.path.isfile(p):
                ret = p
                break

    return ret


def init(conf=None, debug=0, logfile=None, gunicorn=True):
    """Initialize the whole application.

    :param conf: Configuration file to use
    :type conf: str

    :param debug: Enable verbose output
    :type debug: int

    :param logfile: Store the logs in the given file
    :type logfile: str

    :param gunicorn: Enable gunicorn engine instead of flask's default
    :type gunicorn: bool

    :returns: A :class:`Flask` object
    """
    from flask.ext.login import LoginManager, login_user
    from flask.ext.bower import Bower
    from .server import BUIServer as BurpUI
    from .routes import view
    from .api import api, apibp

    # We initialize the core
    bui = BurpUI()

    bui.config['CFG'] = None

    bui.secret_key = 'VpgOXNXAgcO81xFPyWj07ppN6kExNZeCDRShseNzFKV7ZCgmW2/eLn6xSlt7pYAVBj12zx2Vv9Kw3Q3jd1266A=='
    bui.jinja_env.globals.update(isinstance=isinstance, list=list)

    # Then we load our routes
    view.init_bui(bui)
    bui.register_blueprint(view)

    # We initialize the API
    api.init_bui(bui)
    api.version = __version__
    api.release = __release__
    bui.register_blueprint(apibp)

    # And the login_manager
    login_manager = LoginManager()
    login_manager.init_app(bui)
    login_manager.login_view = 'view.login'
    login_manager.login_message_category = 'info'

    bui.config.setdefault('BOWER_COMPONENTS_ROOT', os.path.join('static', 'vendor'))
    bui.config.setdefault('BOWER_REPLACE_URL_FOR', True)
    bower = Bower()
    bower.init_app(bui)

    @login_manager.user_loader
    def load_user(userid):
        """User loader callback"""
        if bui.auth != 'none':
            return bui.uhandler.user(userid)
        return None  # pragma: no cover

    @login_manager.request_loader
    def load_user_from_request(request):
        """User loader from request callback"""
        if bui.auth != 'none':
            creds = request.headers.get('Authorization')
            if creds:
                creds = creds.replace('Basic ', '', 1)
                try:
                    import base64
                    login, password = base64.b64decode(creds).split(':')
                except:
                    pass
                if login:
                    user = bui.uhandler.user(login)
                    if user.active and user.login(login, password):
                        login_user(user)
                        return user

        return None

    # The debug argument used to be a boolean so we keep supporting this format
    if isinstance(debug, bool):
        if debug:
            debug = logging.DEBUG
        else:
            debug = logging.NOTSET
    else:
        levels = [logging.NOTSET, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        if debug >= len(levels):
            debug = len(levels) - 1
        if not debug:
            debug = 0
        debug = levels[debug]

    if debug != logging.NOTSET and not gunicorn:  # pragma: no cover
        bui.config['DEBUG'] = True
        bui.config['TESTING'] = True

    if logfile:
        from logging import Formatter
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(logfile, maxBytes=1024 * 1024 * 100, backupCount=20)
        if debug < logging.INFO:
            LOG_FORMAT = (
                '-' * 80 + '\n' +
                '%(levelname)s in %(module)s.%(funcName)s [%(pathname)s:%(lineno)d]:\n' +
                '%(message)s\n' +
                '-' * 80
            )
        else:
            LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s'
        file_handler.setLevel(debug)
        file_handler.setFormatter(Formatter(LOG_FORMAT))
        bui.logger.addHandler(file_handler)

    # Still need to test conf file here because the init function can be called
    # by gunicorn directly
    bui.config['CFG'] = lookup_config(conf)

    bui.setup(bui.config['CFG'])

    if gunicorn:  # pragma: no cover
        from werkzeug.contrib.fixers import ProxyFix
        bui.wsgi_app = ProxyFix(bui.wsgi_app)

    return bui
