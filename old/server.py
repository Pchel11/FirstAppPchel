import traceback
from http.server import SimpleHTTPRequestHandler
from typing import Optional

from old import utils, custom_types, errors
from old.pages_render import render_hello_page


class MyHttp(SimpleHTTPRequestHandler):
    def handle_theme(self, request: custom_types.HttpRequest) -> None:
        if request.method != "post":
            raise errors.MethodNotAllowed

        response_kwargs = {}
        session = request.session
        if not session:
            session = utils.generate_new_session()
            response_kwargs["session"] = session

        current_theme = utils.load_theme(session)
        new_theme = utils.switch_theme(current_theme)
        utils.store_theme(session, new_theme)

        self.redirect("/hello", **response_kwargs)

    def handle_hello(self, request: custom_types.HttpRequest) -> None:
        if request.method != "get":
            raise errors.MethodNotAllowed

        profile = utils.load_profile(request.session)
        user = custom_types.User.build(profile)

        content = render_hello_page(request, user, user)

        self.respond(content)

    def handle_hello_update(self, request: custom_types.HttpRequest) -> None:
        if request.method != "post":
            raise errors.MethodNotAllowed

        form_data = self.get_form_data()
        new_user = custom_types.User.build(form_data)

        response_kwargs = {}
        session = request.session
        if not session:
            session = utils.generate_new_session()
            response_kwargs["session"] = session

        if new_user.errors:
            saved_data = utils.load_profile(session)
            saved_user = custom_types.User.build(saved_data)
            html = render_hello_page(request, new_user, saved_user)
            self.respond(html, **response_kwargs)
        else:
            utils.store_profile(session, form_data)
            self.redirect("/hello", **response_kwargs)

    def handle_hello_reset(self, request: custom_types.HttpRequest) -> None:
        if request.method != "post":
            raise errors.MethodNotAllowed

        utils.drop_profile(request.session)
        self.redirect("/hello/")

    @staticmethod
    def handle_zde() -> None:
        x = 1 / 0
        print(x)

    def handle_static(self, file_path, content_type) -> None:
        content = utils.read_static(file_path)
        self.respond(content, content_type=content_type)

    def handle_404(self) -> None:
        msg = """NOT FOUND"""
        self.respond(msg, code=404, content_type="text/plain")

    def handle_405(self) -> None:
        self.respond("", code=405, content_type="text/plain")

    def handle_500(self) -> None:
        msg = traceback.format_exc()
        self.respond(msg, code=500, content_type="text/plain")

    def respond(
        self, message, code=200, content_type="text/html", session: Optional[str] = None
    ) -> None:
        payload = utils.to_bytes(message)

        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header_session(session)
        self.end_headers()
        self.wfile.write(payload)

    def redirect(self, to, session: Optional[str] = None) -> None:
        self.send_response(302)
        self.send_header("Location", to)
        self.send_header_session(session)
        self.end_headers()

    def send_header_session(self, session: Optional[str]) -> None:
        if session is None:
            return

        if session:
            header = utils.build_session_header(session)
        else:
            header = utils.build_session_header("expires", expires=True)

        self.send_header("Set-Cookie", header)

    def get_form_data(self) -> str:
        content_length_as_str = self.headers.get("Content-Length", 0)
        content_length = int(content_length_as_str)

        if not content_length:
            return ""

        payload_as_bytes = self.rfile.read(content_length)
        payload = utils.to_str(payload_as_bytes)

        return payload

    def do_GET(self):
        self.dispatch("get")

    def do_POST(self):
        self.dispatch("post")

    def dispatch(self, http_method):
        req = custom_types.HttpRequest.build(
            self.path, method=http_method, headers=self.headers
        )

        endpoints = {
            "/": [self.handle_static, ["index.html", "text/html"]],
            "/0/": [self.handle_zde, []],
            "/hello-reset/": [self.handle_hello_reset, [req]],
            "/hello-update/": [self.handle_hello_update, [req]],
            "/hello/": [self.handle_hello, [req]],
            "/img/": [self.handle_static, [f"images/{req.file_name}", req.content_type]],
            "/s/": [self.handle_static, [f"styles/{req.file_name}", req.content_type]],
            "/theme/": [self.handle_theme, [req]],
        }

        try:
            try:
                handler, args = endpoints[req.normal]
            except KeyError:
                raise errors.NotFound
            handler(*args)
        except errors.NotFound:
            self.handle_404()
        except errors.MethodNotAllowed:
            self.handle_405()
        except Exception:
            self.handle_500()
