# CommunityBotMgmtEndpoint

## Install Dependencies

```
$ sudo apt-get -y install python3-pip
$ sudo pip3 install tornado
```


## TLS Certificate

### Obtain new

Reference:
(Letsencrypt)[https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-16-04]

```
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt-get update
$ sudo aptpget -y install python-certbot
$ sudo certbot certonly --standalone -d [server fully-qualified domain name (e.g., "www.example.com")]
```

Certificate and chain written to `/etc/letsencrypt/live/[domain]/fullchain.pem` 

Key file written to `/etc/letsencrypt/live/[domain]/privkey.pem`


### Renew

System cron job set up in `/etc/cron.d/certbot` to attempt a renew every day

### More info

```
$ cat /etc/letsencrypt/live/[domain]/README
This directory contains your keys and certificates.

`privkey.pem`  : the private key for your certificate.
`fullchain.pem`: the certificate file used in most server software.
`chain.pem`    : used for OCSP stapling in Nginx >=1.3.7.
`cert.pem`     : will break many server configurations, and should not be used
                 without reading further documentation (see link below).
```

## Run


*Note*: `COMMUNITY_BOT_MGMT_ENDPOINT_PORT` is optional and defaults to port 4443 

*Note*: Should not be run on any port below 1024 (aka "well known ports") as that will
require root level permissions for the server

```
# COMMUNITYBOT_MGMT_ENDPOINT_CRTFILE=/path/to/fullchain.pem		\
  COMMUNITYBOT_MGMT_ENDPOINT_KEYFILE=/path/to/privkey.pem 		\
  COMMUNITYBOT_MGMT_ENDPOINT_ENDPOINT_VALIDATION_KEY=abcd	    \
  COMMUNITYBOT_MGMT_ENDPOINT_PORT=4443                          \       
  python3 community-bot-endpoint.py
```
