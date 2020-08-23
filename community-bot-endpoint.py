import tornado.ioloop
import tornado.web
import os
import tornado.tcpserver
import ssl


if 'COMMUNITYBOT_MGMT_ENDPOINT_ENDPOINT_VALIDATION_KEY' not in os.environ:
    print( "FATAL: validation key env var not set")
    sys.exit( 1 )

validation_key = os.environ['COMMUNITYBOT_MGMT_ENDPOINT_ENDPOINT_VALIDATION_KEY']


class CommunityBotHandler(tornado.web.RequestHandler):
    def get( self, operation, operation_validation_key ):
        valid_operations = {
            'start'     : self._doStart,
            'stop'      : self._doStop,
            'restart'   : self._doRestart,
            'update'    : self._doUpdate 
        }

        if operation in valid_operations:
            print( "Valid operation requested: {0}".format(operation) )

            if operation_validation_key == validation_key:
                # Invoke "function pointer"
                valid_operations[ operation ]()
                self.write( { "result": "success" } )
            else:
                error_string = "Incorrect validation key \"{0}\"".format(operation_validation_key)
                self.set_status( 403, error_string )
                self.write( 
                    { 
                        "status"        : "error", 
                        "error_info"    : error_string
                    }
                )
        else:
            error_string = "Invalid operation requested: \"{0}\"".format( operation )
            self.set_status( 404, error_string )
            self.write(
                {
                    "status"        : "error",
                    "error_info"    : error_string
                }
            )



    def _doStart(self):
        print( "Requested operation \"start\" initiated" )


    def _doStop(self):
        print( "Requested operation \"stop\" initiated" )


    def _doRestart(self):
        print( "Requested operation \"restart\" initiated" )


    def _doUpdate(self):
        print( "Requested operation \"update\" initiated" )


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

        print( "FATAL: certificate file or key file not specified as env vars or don't exist on disk")
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

