import hashlib
import json
import sys


def sha256(fname):
    """Compute sha256 hash for file fname"""
    hash_sha256 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def pretty_json(obj):
    """Format an object into json nicely"""
    return json.dumps(obj.json(), separators=(',', ':'), sort_keys=True, indent=2)


def err_and_exit(message, code=1):
    """Write error to STDERR and exit with supplied code"""
    sys.stderr.write(message)
    sys.exit(code)
