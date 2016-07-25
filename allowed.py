import hashlib

LOGINS = (("admin", hashlib.sha512("password").hexdigest()), )
