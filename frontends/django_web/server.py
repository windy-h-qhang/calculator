import os
import threading


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/"

_server_thread = None


def start_server_once(host=DEFAULT_HOST, port=DEFAULT_PORT):
    global _server_thread
    if _server_thread and _server_thread.is_alive():
        return f"http://{host}:{port}/"

    _server_thread = threading.Thread(
        target=run_server,
        args=(host, port),
        daemon=True,
    )
    _server_thread.start()
    return f"http://{host}:{port}/"


def run_server(host, port):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontends.django_web.settings")
    from django.core.wsgi import get_wsgi_application
    from wsgiref.simple_server import WSGIRequestHandler, make_server

    class QuietRequestHandler(WSGIRequestHandler):
        def log_message(self, format, *args):
            return

    application = get_wsgi_application()
    with make_server(host, port, application, handler_class=QuietRequestHandler) as server:
        server.serve_forever()
