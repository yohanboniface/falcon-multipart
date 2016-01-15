from io import open
import os

import falcon
from falcon_multipart.middleware import MultipartMiddleware
import pytest


application = falcon.API(middleware=MultipartMiddleware())


@pytest.fixture
def app():
    return application


def test_parse_form_as_params(client):

    class Resource:

        def on_post(self, req, resp, **kwargs):
            assert req.get_param('simple') == 'ok'
            assert req.get_param('afile').file.read() == b'filecontent'
            assert req.get_param('afile').filename == 'afile.txt'
            resp.body = 'parsed'
            resp.content_type = 'text/plain'

    application.add_route('/route', Resource())

    resp = client.post('/route', data={'simple': 'ok'},
                       files={'afile': ('filecontent', 'afile.txt')})
    assert resp.status == falcon.HTTP_OK
    assert resp.body == 'parsed'


def test_with_binary_file(client):
    here = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(here, 'image.jpg')
    image = open(filepath, 'rb')

    class Resource:

        def on_post(self, req, resp, **kwargs):
            resp.data = req.get_param('afile').file.read()
            resp.content_type = 'image/jpg'

    application.add_route('/route', Resource())

    resp = client.post('/route', data={'simple': 'ok'},
                       files={'afile': image})
    assert resp.status == falcon.HTTP_OK
    image.seek(0)
    assert resp.body == image.read()
