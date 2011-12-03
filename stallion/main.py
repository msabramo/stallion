"""
.. module:: main
   :platform: Unix, Windows
   :synopsis: Main Stallion entry-point.

.. moduleauthor:: Christian S. Perone <christian.perone@gmail.com>

:mod:`main` -- main Stallion entry-point
==================================================================
"""

import sys
import platform

import pkg_resources

from flask import Flask
from flask import render_template
from flask import url_for

from docutils.core import publish_parts

import metadata

import __init__ as stallion

app = Flask(__name__)

class Crumb(object):
    def __init__(self, title, href="#"):
        self.title = title
        self.href = href

def get_shared_data():
    shared_data = {}
    shared_data["distributions"] = [d for d in pkg_resources.working_set]

    return shared_data

@app.route('/')
def index():
    data = {}
    data["breadpath"] = [Crumb("Main")]
    
    data.update(get_shared_data())
    data["menu_home"] = "active"

    sys_info = {}
    sys_info["Python Platform"] = sys.platform
    sys_info["Python Version"] = sys.version
    sys_info["Python Prefix"] = sys.prefix
    sys_info["Machine Type"] = platform.machine()
    sys_info["Platform"] = platform.platform()
    sys_info["Processor"] = platform.processor()
    sys_info["Python Implementation"] = platform.python_implementation()
    sys_info["System"] = platform.system()
    sys_info["System Arch"] = platform.architecture()

    data["system_information"] = sys_info

    return render_template('system_information.html', **data)

@app.route('/about')
def about():
    data = {}
    data.update(get_shared_data())
    data["menu_about"] = "active"

    data["breadpath"] = [Crumb("About")]
    data["version"] = stallion.__version__
    data["author"] = stallion.__author__
    data["author_url"] = stallion.__author_url__

    return render_template('about.html', **data)

@app.route('/distribution/<dist_name>')
def distribution(dist_name=None):
    pkg_dist = pkg_resources.get_distribution(dist_name)

    data = {}
    data.update(get_shared_data())

    data["dist"] = pkg_dist
    data["breadpath"] = [Crumb("Main", url_for('index')), Crumb("Package"), Crumb(pkg_dist.project_name)]

    settings_overrides = {
        'raw_enabled': 0, # no raw HTML code
        'file_insertion_enabled': 0, # no file/URL access
        'halt_level': 2, # at warnings or errors, raise an exception
        'report_level': 5, # never report problems with the reST code
    }

    pkg_metadata = pkg_dist.get_metadata(metadata.METADATA_NAME)
    parsed, key_known = metadata.parse_metadata(pkg_metadata)
    distinfo = metadata.metadata_to_dict(parsed, key_known)
    
    parts = None
    try:
        parts = publish_parts(source = distinfo["description"],
                              writer_name = 'html', settings_overrides = settings_overrides)
    except:
        pass

    data["distinfo"] = distinfo

    print distinfo["metadata-version"]

    if parts is not None:
        data["description_render"] = parts["body"]
    
    return render_template('distribution.html', **data)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')