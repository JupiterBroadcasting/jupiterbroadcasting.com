#!/bin/bash

# <UDF name="registry_host" label="hostname for registry to be hosted at"  example="registry.example.com" />
# <UDF name="host_root" label="root domain for where registry is going to be installed"  example="example.com" />
# <UDF name="registry_username" label="username to auth against docker registry" example="my-username" />
# <UDF name="registry_password" label="password to auth against docker registry" example="my-password" />
# <UDF name="registry_email" label="email address to register tls certs for" example="foo@example.com" />
# <UDF name="CLI_TOKEN" label="linode personal access token used to create A record for registry domain" />

exec > >(tee -i /var/log/stackscript.log)

mkdir -p ~/.config
echo "
[DEFAULT]
default-user = user

[user]
token = $CLI_TOKEN
region = us-east
type = g6-nanode-1
image = linode/almalinux8
" > ~/.config/linode-cli

# Install linode-cli and set A record for registry domain
echo "installing python3-pip"
apt update -y
apt install -y python3-pip
pip3 install linode-cli

linode-cli account view
echo "looking for $HOST_ROOT"
linode-cli domains list --text --format 'id,domain'  --no-headers   | grep $HOST_ROOT | awk '{ print $1 }'
domain_id=$(linode-cli domains list --text --format 'id,domain' --no-headers   | grep $HOST_ROOT | awk '{ print $1 }')
echo "domain_id $domain_id"
my_ip=$(hostname -I | awk '{print $1}')
echo "my_ip $my_ip"

echo "domain_id $domain_id"
echo "creating A record"
linode-cli domains records-create $domain_id --type A --name $REGISTRY_HOST --target $my_ip

echo "sleeping to wait for A record to populate"
sleep 1m

# Generate LetsEncrypt certs
echo "generating certs"
apt install certbot -y
certbot certonly --keep-until-expiring --standalone -d $REGISTRY_HOST --non-interactive --agree-tos -v --email $REGISTRY_EMAIL

echo "creating combined certs"
cd /etc/letsencrypt/live/$REGISTRY_HOST/
cp privkey.pem domain.key
cat cert.pem chain.pem > domain.crt
chmod 777 domain.crt
chmod 777 domain.key


Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh


#Setup cron job to renew certs
echo "setting up cron job"
line="30 2 * * 1 certbot renew >> /var/log/letsencrypt-renew.log"
(crontab -u root -l; echo "$line" ) | crontab -u root -

# Generate encrypted password file for auth
echo "generating password file"
cd
mkdir auth
docker run --rm  --mount type=bind,source="$(pwd)"/auth,target=/auth --entrypoint htpasswd httpd:2 -Bbn $REGISTRY_USERNAME $REGISTRY_PASSWORD > auth/htpasswd


echo "running registry image"
# Run registry docker image
docker run -d -p 443:5000 --restart=always --name registry \
  -v /etc/letsencrypt/live/$REGISTRY_HOST:/certs \
  -v /opt/docker-registry:/var/lib/registry \
  -v `pwd`/auth:/auth \
  -e "REGISTRY_AUTH=htpasswd" \
  -e "REGISTRY_AUTH_HTPASSWD_REALM=Axway Docker Registry" \
  -e REGISTRY_STORAGE=s3 \
  -e REGISTRY_STORAGE_S3_REGION=$S3_REGION \
  -e REGISTRY_STORAGE_S3_BUCKET="kp-registry" \
  -e REGISTRY_STORAGE_S3_REGIONENDPOINT=$S3_REGIONENDPOINT \
  -e REGISTRY_STORAGE_S3_SECURE=true \
  -e REGISTRY_STORAGE_S3_ACCESSKEY=$S3_ACCESSKEY \
  -e REGISTRY_STORAGE_S3_SECRETKEY=$S3_SECRETKEY \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  registry:2