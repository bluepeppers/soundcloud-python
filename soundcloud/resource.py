import sys

try:
    import json
except ImportError:
    import simplejson as json

if sys.version_info < (3, 0):
    from UserList import UserList
else:
    UserList = list

class Resource(object):
    """Object wrapper for resources.

    Provides an object interface to resources returned by the Soundcloud API.
    """
    def __init__(self, obj):
        self.obj = obj

    def __getstate__(self):
        return self.obj.items()

    def __setstate__(self, items):
        if not hasattr(self, 'obj'):
            self.obj = {}
        for key, val in items:
            self.obj[key] = val

    def __getattr__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        raise AttributeError

    def fields(self):
        return self.obj

    def keys(self):
        return self.obj.keys()


class ResourceList(UserList):
    """Object wrapper for lists of resources."""
    def __init__(self, resources=[]):
        data = [Resource(resource) for resource in resources]
        super(ResourceList, self).__init__(data)


def wrapped_resource(response):
    """Return a response wrapped in the appropriate wrapper type.

    Lists will be returned as a ```ResourceList``` instance,
    dicts will be returned as a ```Resource``` instance.
    """
    try:
        try:
            content = json.loads(response.content.decode("utf-8"))
        except (UnicodeError, AttributeError):
            content = json.loads(response.content)
    except ValueError:
        # not JSON
        content = response.content
    if isinstance(content, list):
        result = ResourceList(content)
    else:
        result = Resource(content)
    result.raw_data = response.content

    for attr in ('url', 'status_code', 'reason'):
        setattr(result, attr, getattr(response, attr))

    return result
