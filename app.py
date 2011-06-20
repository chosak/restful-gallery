# App Engine now requires Django version to be set explicitly.
# http://code.google.com/appengine/docs/python/tools/libraries.html#Django
from google.appengine.dist import use_library
use_library('django', '0.96')

import config

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from util import api_call, render_template, read_json, write_json, write_image
from models import Shareable, Album, Image

# from auth import verify_auth, AuthHandler
# api_call.auth = verify_auth(error_code=401)

class AlbumRootHandler(webapp.RequestHandler):
    @api_call(config.ALBUM_ROOT_URL, 'List existing albums')
    def get(self):
        """GET handler for gallery albums.

        URL pattern: /albums
        
        Returns 200 OK with JSON data structure containing list of albums.
        Returns Content-type: application/json.

        Returns 401 UNAUTHORIZED to all calls if authorization fails.
        """
        write_json(self, [album.to_dict() for album in Album.all()]) 

    @api_call(config.ALBUM_ROOT_URL, 'Create a new empty album', { 'name': 'text' })
    def post(self):
        """POST handler for gallery albums.

        URL pattern: /albums
        POST data must contain album metadata: 'name'.

        Returns 201 CREATED with JSON data structure describing new album.
        Returns Content-type: application/json.
        Also returns Location header pointing to API URL for album details.
        
        Include 'wrapjson' parameter in POST to wrap returned JSON in
        a <textarea>. This also changes the returned Content-type to text/html.

        If request is poorly formatted returns 400 BAD REQUEST.

        Returns 401 UNAUTHORIZED to all calls if authorization fails.
        """
        try:
            data = dict(((str(k), v) for k, v in self.request.POST.items()))
            album = Album(album_id=config.ALBUM_ID_GENERATOR(),
                          **data)
        except:
            data = {}
            self.error(400)
        else:
            if not config.DEMO_MODE:
                album.put() 

            data = album.to_dict()
            self.response.headers['Location'] = data['url']
            self.response.set_status(201)
        
        write_json(self, data, wrapjson='wrapjson' in self.request.POST)

class AlbumHandler(webapp.RequestHandler):
    @api_call(config.ALBUM_URL_TEMPLATE_STRING, 'Get information about an album')
    def get(self, album_id):
        """GET handler for a particular gallery album.

        URL pattern: /albums/${album_id}
        
        If album exists, returns 200 OK with JSON album data structure.
        Returns Content-type: application/json.
        If album doesn't exist, returns 404 NOT FOUND.

        Returns 401 UNAUTHORIZED to all calls if authorization fails.
        """
        q = Album.all().filter('album_id =', album_id)
        album = q.get()
        if not album:
            return self.error(404)

        write_json(self, album.to_dict())

    @api_call(config.ALBUM_URL_TEMPLATE_STRING, 'Delete an album')
    def delete(self, album_id):
        """DELETE handler for gallery album.

        URL pattern: /albums/${album_id}
        
        If album exists, returns 200 OK. 
        If album doesn't exist, returns 404 NOT FOUND.

        Also deletes all images associated with this album.

        Returns 401 UNAUTHORIZED to all calls if authorization fails.
        """
        q = Album.all().filter('album_id =', album_id)
        album = q.get()
        if not album:
            return self.error(404)

        if not config.DEMO_MODE:
            q = Image.all().filter('album =', album)
            for image in q:
                image.delete()

            album.delete()

class ImageRootHandler(webapp.RequestHandler):
    @api_call(config.IMAGE_ROOT_URL_TEMPLATE_STRING, 'List all images in an album')
    def get(self, album_id):
        """GET handler for images in a particular gallery album.

        URL pattern: /albums/${album_id}/images
        
        If album exists, returns 200 OK with JSON image data structure.
        Returns Content-type: application/json.
        If album doesn't exist, returns 404 NOT FOUND.

        Returns 401 UNAUTHORIZED to all calls if authorization fails.
        """
        q = Album.all().filter('album_id =', album_id)
        album = q.get()
        if not album:
            return self.error(404)

        images = Image.all().filter("album =", album)
        write_json(self, [image.to_dict() for image in images])

    @api_call(config.IMAGE_ROOT_URL_TEMPLATE_STRING, 'Add an image to an album', { 'name': 'text', 'file': 'file' })
    def post(self, album_id):
        """POST handler for a gallery image.

        URL pattern: /albums/${album_id}/images
        POST data must be of type multipart/form and contain image as 'file'.
        POST data must also contain image metadata: 'name'.
        Image filename must include an extension.

        Returns 201 CREATED with JSON data structure describing new image.
        Returns Content-type: application/json.
        Also returns Location header pointing to API URL for image details.

        Include 'wrapjson' parameter in POST to wrap returns JSON in
        a <textarea>. This also changes the returned Content-type to text/html.

        If album doesn't exist, returns 404 NOT FOUND.
        If request is poorly formatted returns 400 BAD REQUEST.

        Returns 401 UNAUTHORIZED to all calls if authorization fails.
        """
        q = Album.all().filter('album_id =', album_id)
        album = q.get()
        if not album:
            return self.error(404)

        try:
            data = dict(((str(k), v) for k, v in self.request.POST.items()))
            if 'file' in data:
                data['extension'] = data['file'].filename.split('.')[-1].lower()
                if data['extension'] == data['file'].filename:
                    data['extension'] = ''
                else:
                    data['extension'] = '.' + data['extension']
                data['image_data'] = data['file'].file.read()

            image = Image(image_id=config.IMAGE_ID_GENERATOR(),
                          album=album,
                          **data)
        except:
            data = {}
            self.error(400)
        else:
            if not config.DEMO_MODE:
                image.put()

            data = image.to_dict()
            self.response.headers['Location'] = data['url']
            self.response.set_status(201)

        write_json(self, data, wrapjson='wrapjson' in self.request.POST)

class ImageHandler(webapp.RequestHandler):
    @api_call(config.IMAGE_URL_TEMPLATE_STRING, 'Get information about an image')
    def get(self, album_id, image_id, extension=None):
        """GET handler for GGB image metadata and files.

        URL pattern: /albums/${album_id}/images/${image_id}(${extension})

        If called without a file extension:
            If image exists, returns 200 OK with JSON image data structure.
            Returns Content-type: application/json.
            If image doesn't exist, returns 404 NOT FOUND.
        
        If called with a file extension:
            If image exists and has the matching extension, returns the image.
            Returned Content-type matches the image format.
            Otherwise returns 404 NOT FOUND.
       
        Returns 401 UNAUTHORIZED to all calls if authorization fails.
        """
        q = Album.all().filter('album_id =', album_id)
        album = q.get()
        if not album:
            return self.error(404)

        q = Image.all().filter('album =', album).filter('image_id =', image_id)
        image = q.get()
        if not image:
            return self.error(404)

        if not extension:
            data = image.to_dict()
            return write_json(self, image.to_dict())
        
        if extension != image.extension:
            return self.error(404)
   
        write_image(self, image.image_data, image.extension)

    @api_call(config.IMAGE_URL_TEMPLATE_STRING, 'Delete an image')
    def delete(self, album_id, image_id, extension=None):
        """DELETE handler for gallery images.

        URL pattern: /albums/${album_id}/images/${image_id}
        
        If image exists, returns 200 OK. 
        If image doesn't exist, returns 404 NOT FOUND.

        Returns 401 UNAUTHORIZED to all calls if authorization fails.
        """
        q = Album.all().filter('album_id =', album_id)
        album = q.get()
        if not album:
            return self.error(404)

        q = Image.all().filter('album =', album).filter('image_id =', image_id)
        image = q.get()
        if not image:
            return self.error(404)
        
        if extension and extension != image.extension:
            return self.error(404)

        if not config.DEMO_MODE:
            image.delete()

class ShareHandler(webapp.RequestHandler):
    def get(self, hash, extension=None):
        q = Album.all().filter('hash =', hash)
        album = q.get()
        if album:
            if extension:
                return self.error(404)
            
            q = Image.all().filter('album =', album)
            return self.response.out.write(render_template('album.html', {
                'name': album.name,
                'images': q,
            }))

        q = Image.all().filter('hash =', hash)
        image = q.get()
        if image:
            if not extension:
                return self.response.out.write(render_template('image.html',
                    { 'image': image }))
            elif image.extension == extension:
                return write_image(self, image.image_data, extension)
            else:
                return self.error(404)
        
        return self.error(404)

class AdminHandler(webapp.RequestHandler):
   def get(self):
        self.response.out.write(render_template('admin.html', { 
            'api_calls': api_call.calls,
            'demo_mode': config.DEMO_MODE, 
        }))

class DefaultHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)

wsgi_paths = [
    (config.IMAGE_URL_REGEX, ImageHandler),
    (config.IMAGE_ROOT_URL_REGEX, ImageRootHandler),
    (config.ALBUM_URL_REGEX, AlbumHandler),
    (config.ALBUM_ROOT_URL, AlbumRootHandler),
    (config.SHARE_URL_REGEX, ShareHandler),
    (config.ADMIN_URL, AdminHandler),
    ('/.*', DefaultHandler),
]

def main():
    run_wsgi_app(webapp.WSGIApplication(wsgi_paths, debug=True))
	
if __name__ == "__main__":
    main()

