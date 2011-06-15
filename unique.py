# Adapted from http://squeeville.com/2009/01/30/add-a-unique-constraint-to-google-app-engine/
from google.appengine.ext import db

class UniqueConstraintViolation(Exception):
    def __init__(self, scope):
        super(UniqueConstraintViolation, self).__init__('Could not create unique value within scope \'%s\'.' % scope)

class Unique(db.Model):
    @classmethod
    def new(cls, scope, generator, attempts=1):
        def txn(scope, value):
            key_name = "%s:%s:%s" % (Unique.__name__, scope, value)
            if not Unique.get_by_key_name(key_name):
                unique = Unique(key_name=key_name)
                return unique.put()

        for i in range(attempts):
            value = generator()
            if db.run_in_transaction(txn, scope, value):
                return value

        raise UniqueConstraintException(scope)

