#!/usr/bin/python

import random
import sys
import uuid
from base36 import base36encode
from string import Template

# URL for web-based gallery administration
ADMIN_URL = '/admin'

# URL prefix for all gallery albums
ALBUM_ROOT_URL = '/albums'

# Template to generate an album API URL
ALBUM_URL_TEMPLATE_STRING = ALBUM_ROOT_URL + '/${album_id}'
ALBUM_URL_TEMPLATE = Template(ALBUM_URL_TEMPLATE_STRING)

# Generator and matching regex for album IDs
ALBUM_ID_GENERATOR = lambda: str(uuid.uuid4())
ALBUM_ID_REGEX = r'([\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})'

# URL regex for all albums
ALBUM_URL_REGEX = ALBUM_URL_TEMPLATE.substitute({'album_id': ALBUM_ID_REGEX}) 

# URL component for an album image root
IMAGE_RELATIVE_URL = 'images'

# Template to generate an API URL for an album image root
IMAGE_ROOT_URL_TEMPLATE_STRING = ALBUM_URL_TEMPLATE_STRING + '/' + IMAGE_RELATIVE_URL
IMAGE_ROOT_URL_TEMPLATE = Template(IMAGE_ROOT_URL_TEMPLATE_STRING)

# URL regex for all album image roots
IMAGE_ROOT_URL_REGEX = IMAGE_ROOT_URL_TEMPLATE.substitute({'album_id': ALBUM_ID_REGEX})

# Template to generate an image API URL
IMAGE_URL_TEMPLATE_STRING = IMAGE_ROOT_URL_TEMPLATE_STRING + '/${image_id}'
IMAGE_URL_TEMPLATE = Template(IMAGE_URL_TEMPLATE_STRING)

# Generator and matching regex for image IDs
IMAGE_ID_GENERATOR = lambda: str(uuid.uuid4())
IMAGE_ID_REGEX = r'([\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})'

# Regex for valid file extensions
FILE_EXT_REGEX = r'(\.(?:BMP|bmp|JPG|jpg|JPEG|jpeg|PNG|png))?'

# URL regex for all images
IMAGE_URL_REGEX = IMAGE_URL_TEMPLATE.substitute({'album_id': ALBUM_ID_REGEX, 
                                                 'image_id': IMAGE_ID_REGEX + FILE_EXT_REGEX})

# URL prefix for all shareable items
SHARE_ROOT_URL = '/share'

# Function to generate a random index for all shareable items
SHARE_INDEX_GENERATOR = lambda: random.randint(0, sys.maxint)

# Template to generate a shareable URL
SHARE_URL_TEMPLATE_STRING = SHARE_ROOT_URL + '/${hash}'
SHARE_URL_TEMPLATE = Template(SHARE_URL_TEMPLATE_STRING)

# Generator and matching regex for shareable URL hashes
SHARE_HASH_GENERATOR = lambda index: base36encode(index)
SHARE_HASH_REGEX = r'([0-9a-z]{1,6})'

# URL regex for all shareable items
SHARE_URL_REGEX = SHARE_URL_TEMPLATE.substitute({'hash': SHARE_HASH_REGEX + FILE_EXT_REGEX})

