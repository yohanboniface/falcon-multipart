from .parser import Parser


class MultipartMiddleware(object):

    def __init__(self, parser=None):
        self.parser = parser or Parser

    def parse(self, stream, environ):
        return self.parser(fp=stream, environ=environ)

    def process_request(self, req, resp, **kwargs):

        if 'multipart/form-data' not in (req.content_type or ''):
            return

        # This must be done to avoid a bug in cgi.FieldStorage.
        req.env.setdefault('QUERY_STRING', '')

        form = self.parse(stream=req.stream, environ=req.env)
        for key in form:
            field = form[key]
            if not getattr(field, 'filename', False):
                field = form.getlist(key)
            # TODO: put files in req.files instead when #493 get merged.
            req._params[key] = field
