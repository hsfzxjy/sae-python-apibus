from requests import fetch_API

__all__ = ['APIFetcher']

class APIFetcher(object):

    API_URL_MAPPING = {
        'get_log': {
            'url': '/log/{service}/{date}/{ident}.log?{fop}',
            'optional': ['fop'],
        },
    }

    def __init__(self):
        self._args = {}

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        self._args.clear()

    def set_args(self, **kwargs):
        self._args.update(kwargs)

        return self

def bind_method(name):

    config = APIFetcher.API_URL_MAPPING[name]
    raw_url = config['url']

    def _call_API(self, **kwargs):
        arguments = { key: '' for key in config.get('optional', []) }
        print dir(self)
        arguments.update(self._args)
        arguments.update(kwargs)

        return fetch_API(raw_url.format(**arguments))

    setattr(APIFetcher, name, _call_API)

for name in APIFetcher.API_URL_MAPPING.iterkeys():
    bind_method(name)