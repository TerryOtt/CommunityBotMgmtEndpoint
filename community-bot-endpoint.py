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
    if 'COMMUNITYBOT_MGMT_ENDPOINT_CRTFILE' not in os.environ or                            \
            os.path.isfile( os.environ['COMMUNITYBOT_MGMT_ENDPOINT_CRTFILE'] ) is False or  \
            'COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE' not in os.environ or                       \
            os.path.isfile( os.environ['COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE'] ) is False:

        print( "No keyfile at {0}".format(os.environ['COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE']) )
        sys.exit( 1 )

    crt_file = os.environ['COMMUNITYBOT_MGMT_ENDPOINT_CRTFILE']
    key_file = os.environ['COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE']

    print( "TLS certificate and chain: {0}\n     TLS private key file: {1}".format(crt_file, key_file) )

    ssl_ctx.load_cert_chain( crt_file, key_file ) 

    return ssl_ctx


if __name__ == "__main__":
    application = _make_app()
    ssl_ctx = _make_ssl_ctx()

    http_server = tornado.httpserver.HTTPServer( application, ssl_options=ssl_ctx )

    server_port = int( os.environ.get( 'COMMUNITYBOT_MGMT_ENDPOINT_PORT', 4443 ) )

    http_server.listen( server_port )

    print( "Listening on port {0}".format(server_port) )

    tornado.ioloop.IOLoop.current().start()

