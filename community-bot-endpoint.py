import tornado.ioloop
import tornado.web
import os
import tornado.tcpserver
import pathlib
import ssl


class CommunityBotHandler(tornado.web.RequestHandler):
    def get( self, operation, operation_validation_key ):
        self.write("Endpoint: {0}, Endpoint key: {1}".format(operation, operation_validation_key) )


def _make_app():
    return tornado.web.Application(
        [
            (r"^\/bot\/(.*?)\/(.*?)\s*$", CommunityBotHandler),
        ]
    )


def _make_ssl_ctx():
    ssl_ctx = ssl.create_default_context( ssl.Purpose.CLIENT_AUTH )
    ssl_ctx.load_cert_chain(
        pathlib.Path( os.environ['COMMUNITYBOT_MGMT_ENDPOINT_CRTFILE'] ),
        pathlib.Path( os.environ['COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE'] )
    )

    return ssl_ctx


if __name__ == "__main__":
    application = _make_app()
    ssl_ctx = _make_ssl_ctx()

    http_server = tornado.httpserver.HTTPServer( application, ssl_options=ssl_ctx )

    server_port = os.environ.get( 'COMMUNITYBOT_MGMT_ENDPOINT_PORT', 443 )

    application.listen( server_port )

    tornado.ioloop.IOLoop.current().start()
