import cgi
import oauth2 as oauth  # https://github.com/simplegeo/python-oauth2

def get_secret_for_consumer(consumer):
    """Given an API user, return the associated secret."""
    if 'test-consumer' == consumer:
        return 'test-secret'

    # Implement more advanced access control here.
    raise ValueError(consumer)
        
class TwoLeggedOAuth(object):
    scheme = 'OAuth'
    server = oauth.Server({ 'HMAC-SHA1': oauth.SignatureMethod_HMAC_SHA1() })

    @classmethod
    def authenticate(cls, request):
        # Copy params and remove any POSTed files from the list.
        params = dict([(k,v) for k,v in request.params.iteritems() if not isinstance(v, cgi.FieldStorage)])   
        # Create the OAuth request and consumer objects, and try to verify.
        oauth_request = oauth.Request.from_request(
            http_method=request.method,
            http_url=request.url,
            headers=request.headers,
            parameters=params,
            query_string=request.query_string)

        consumer = params['oauth_consumer_key']
        oauth_consumer = oauth.Consumer(
            key=consumer, 
            secret=get_secret_for_consumer(consumer))
                
        cls.server.verify_request(oauth_request, oauth_consumer, None)

def verify_auth(auth_cls=TwoLeggedOAuth, error_code=401):
    def wrapper(method):
        def authenticate(handler, *args, **kwargs): 
            try:
                auth_cls.authenticate(handler.request)
            except Exception, e:
                handler.response.headers['WWW-Authenticate'] = auth_cls.scheme
                return handler.error(error_code)
            
            return method(handler, *args, **kwargs)
        return authenticate
    return wrapper

