import cgi
import datetime
import os
import re

from google.appengine.ext.webapp import template
from django.utils import simplejson as json

def api_call(url_template, description, post_dict={}):
    def wrapper(method):
        api_call.calls.append({ 'url_template': url_template,
                                'url_parameters': re.findall(r'(?<=\$\{)[\w\-]+(?=\})', url_template),
                                'method_type': method.__name__.upper(),
                                'description': description,
                                'doc': cgi.escape(method.__doc__),
                                'post_dict': post_dict})
        return api_call.auth(method) if api_call.auth else method
    return wrapper

api_call.calls = []
api_call.auth = None

def render_template(filename, values={}):
    """Helper function for rendering an HTML template."""
    templateFilename = os.path.join(os.path.dirname(__file__), 'templates/' + filename)
    if not os.path.isfile(templateFilename):
        return None
    return template.render(templateFilename, values)

def read_json(*args, **kwargs):
    """Helper function for reading in JSON data."""
    return json.loads(*args, **kwargs)

def write_json(self, d, wrapjson=False):
    """Helper function for writing out JSON data."""
    json_str = str(json.dumps(d, cls=JSONEncoder))
    
    if not wrapjson:
        self.response.headers['Content-type'] = 'application/json'
        self.response.out.write(json_str)
    else:
        # In certain cases, such as when JSON is being returned to a browser iframe,
        # it might be necessary to wrap the returned data in a <textarea> element,
        # and also change the Content-type to text/html. This is because JSON can
        # contain characters which won't be interpreted by browsers properly, and
        # allows for a better response to AJAX requests.
        #
        # The 'status' and 'statusText' attributes are added so that browser-based
        # file uploads that use an iframe can accurately get the status code.
        self.response.headers['Content-type'] = 'text/html'
        self.response.out.write('<textarea status="%s" statusText="%s">%s</textarea>' % 
            (self.response.status, 
             self.response.status_message,
             json_str))

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)

def write_image(self, image, extension):
    """Helper function for writing out a binary image."""
    self.response.headers['Content-Type'] = str(get_content_type(extension))
    self.response.out.write(image)

def get_content_type(extension):
    """Map a file's extension to its HTTP content type."""
    extension = extension.lower()
    if extension == 'bmp':
        return 'Content-type: image/bmp'
    elif extension == 'jpg' or extension == 'jpeg':
        return 'Content-type: image/jpeg'
    elif extension == 'png':
        return 'Content-type: image/png'
    elif extension == 'tif' or extension == 'tiff':
        return 'Content-type: image/tiff'
    elif extension == 'gif':
        return 'Content-type: image/gif'
    else:
        return 'Content-type: text/plain'

