import tornado.ioloop
import tornado.web
import os
import tornado.tcpserver
import ssl
import logging
import subprocess


if 'COMMUNITYBOT_MGMT_ENDPOINT_ENDPOINT_VALIDATION_KEY' not in os.environ:
    logging.fatal( "Validation key env var not set")
    sys.exit( 1 )

validation_key = os.environ['COMMUNITYBOT_MGMT_ENDPOINT_ENDPOINT_VALIDATION_KEY']

communitybot_supervisorctl_name = "communitybot-discord"


class CommunityBotHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin",      "*")
        self.set_header("Access-Control-Allow-Headers",     "x-requested-with")
        self.set_header('Access-Control-Allow-Methods',     "GET, OPTIONS")


    def options(self):
        # no body
        self.set_status(204)
        self.finish()


    def get( self, operation, operation_validation_key ):
        valid_operations = {
            'start'     : self._doStart,
            'stop'      : self._doStop,
            'restart'   : self._doRestart,
            'update'    : self._doUpdate 
        }

        if operation in valid_operations:
            logging.info( "Valid operation requested: {0}".format(operation) )

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


    # All operations taken from CommunityBot documentation:
    #       https://wazeopedia.waze.com/wiki/USA/CommunityBot/BuildRun

    def _doStart(self):
        logging.info( "Requested operation \"start\" initiated" )
        subprocess.run( [ "supervisorctl", "start", communitybot_supervisorctl_name ] )


    def _doStop(self):
        logging.info( "Requested operation \"stop\" initiated" )
        subprocess.run( [ "supervisorctl", "stop", communitybot_supervisorctl_name ] )


    def _doRestart(self):
        logging.info( "Requested operation \"restart\" initiated" )
        subprocess.run( [ "supervisorctl", "restart", communitybot_supervisorctl_name ] )


    def _doUpdate(self):
        logging.info( "Requested operation \"update\" initiated" )

        # Change current directory
        bot_codedir = '/home/communitybot/CommunityBot'
        os.chdir( bot_codedir )

        # Show current directory
        curr_dir = os.getcwd()
        print( "current dir: {0}".format(curr_dir) )

        if curr_dir != bot_codedir:
            logging.error( "Not in proper dir for update even after change, bailing" )
            return
            
        # stop the bot
        self._doStop()
        
        # Download new code with git *as communitybot user*
        subprocess.run( [ "su", "-c git pull", "communitybot" ] )

        # Build new code *as community bot*
        subprocess.run( [ "su", "-c dotnet build -c Release", "communitybot" ] ) 

        # Publish the code *as communitybot*
        subprocess.run( [ "su", "-c dotnet publish -c Release", "communitybot" ] )

        # Start the bot
        self._doStart()


def _make_app():
    return tornado.web.Application(
        [
            (r"^\/bot\/(.*?)\/(.*?)\s*$", CommunityBotHandler),
        ],
        debug=True
    )


def _make_ssl_ctx():
    ssl_ctx = ssl.create_default_context( ssl.Purpose.CLIENT_AUTH )
    if 'COMMUNITYBOT_MGMT_ENDPOINT_CRTFILE' not in os.environ or                            \
            os.path.isfile( os.environ['COMMUNITYBOT_MGMT_ENDPOINT_CRTFILE'] ) is False or  \
            'COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE' not in os.environ or                       \
            os.path.isfile( os.environ['COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE'] ) is False:

        logging.fatal( "Certificate file or key file not specified as env vars or don't exist on disk")
        sys.exit( 1 )

    crt_file = os.environ['COMMUNITYBOT_MGMT_ENDPOINT_CRTFILE']
    key_file = os.environ['COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE']

    logging.info( "TLS certificate and chain: {0}\n     TLS private key file: {1}".format(crt_file, key_file) )

    # Set minimum TLS version to 1.2 to improve SSL Labs SSL score

    # Cannot use minimum_version as Ubuntu 16.04 has OpenSSL < 1.1.0 installed
    #ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    # Using recommended doc example from https://docs.python.org/3/library/ssl.html#protocol-versions
    ssl_ctx.options |= ssl.OP_NO_TLSv1
    ssl_ctx.options |= ssl.OP_NO_TLSv1_1

    # limiting cipher suites to the only two SSL labs approves of
    #       1. TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    #       2. TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256

    # https://docs.python.org/2/library/ssl.html#ssl.SSLContext.set_ciphers
    # IDs are colon-separated
    # Recommended list obtained from https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices
    #ssl_ctx.set_ciphers( "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256" )

    acceptable_cipher_suites = [
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        #"ECDHE-ECDSA-AES128-SHA",
        #"ECDHE-ECDSA-AES256-SHA",
        #"ECDHE-ECDSA-AES128-SHA256",
        #"ECDHE-ECDSA-AES256-SHA384",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES256-GCM-SHA384",
        #"ECDHE-RSA-AES128-SHA",
        #"ECDHE-RSA-AES256-SHA",
        #"ECDHE-RSA-AES128-SHA256",
        #"ECDHE-RSA-AES256-SHA384",
        "DHE-RSA-AES128-GCM-SHA256",
        "DHE-RSA-AES256-GCM-SHA384",
        #"DHE-RSA-AES128-SHA",
        #"DHE-RSA-AES256-SHA",
        #"DHE-RSA-AES128-SHA256",
        #"DHE-RSA-AES256-SHA256",
    ]

    ssl_ctx.set_ciphers( ":".join(acceptable_cipher_suites) )


    ssl_ctx.load_cert_chain( crt_file, key_file ) 

    return ssl_ctx


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    application = _make_app()
    ssl_ctx = _make_ssl_ctx()

    http_server = tornado.httpserver.HTTPServer( application, ssl_options=ssl_ctx )

    server_port = int( os.environ.get( 'COMMUNITYBOT_MGMT_ENDPOINT_PORT', 443 ) )

    http_server.listen( server_port )

    logging.info( "Listening for HTTPS connections on port {0}".format(server_port) )

    tornado.ioloop.IOLoop.current().start()
