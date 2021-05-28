# AD-gravatar-bridge
a small set of tools to create a gravatar like rest api to access Thumbnail Pictures stored in the Active Directory

## Q&A
### What dose this repository do?
This repository enables you to access the Thumbnail Pictures of users in your Active Directory like there are stored on [gravatar](https://gravatar.com)

### Why do I need this?
I needed this to display Thumbnail Pictures of users during a Jitsi-meet conference on an internal Jitsi-server. But maybe you will find this interesting or find usage of this for a different application

### how dose it work?
This Tool consist of two parts:
1. a Python Script for downloading the Pictures to a local folder
2. a NGINX server for serving the Thumbnail Pictures

The Python script will download all the Thumbnails in your AD and store them in a folder. Next it will md5-hash the corresponding email-address for each Thumbnail. This Script must be run periodicly. The NGINX-server will then simply serve the files when one is requested.

## Installation
I will list steps for installing on an Ubuntu server, but you could adapt these and install it on Windows, Macos, etc.

First you need to install `python`, `pip`, `git` and `NGINX`
```bash
sudo apt install nginx python3 git
```

Then you need to install `python-ldap` and `hashlib`. The installtion of `python-ldap` can be a little tricky so first install some dependencies
```bash
sudo apt install libsasl2-dev python-dev libldap2-dev libssl-dev
```
and then install the package
```bash
pip install python-ldap hashlib
```
After that you can clone this repo to a location of your choise. In this example I use `/opt/`. so
```bash
cd /opt
git clone https://github.com/theodor-franke/AD-gravatar-bridge.git
cd Ad-gravarar-bridge
```
next create a folder where you want to store the Images. I chose `/var/www/avatrs`
```bash
mkdir /var/www/avatars
```
Now you need to edit some settings in the `ad-gravatar-bridge.py` file, so open this file and adjust the values.

``` python
# Your LDAP server
SERVER = 'ldap://example.com'

# A service-user for accessing LDAP
USERNAME = 'cn=servldap,ou=ServiceUser,dc=example,dc=com'
PASSWORD = 'S3CR3T'

# A query for filtering the LDAP
BASE_DN = 'OU=Users,DC=example,DC=com'

# Avatar Location
AVATAR_LOCATION = '/var/www/avatars'

```

At this point you can test if the crawling of the data works, simply type the following command. If everything works you souhld get image-files in the folder you specified with jiberish looking names.

``` bash
python3 ad-gravatar-bridge.py
```

Now you need to configure your NGINX-server to serve these files. Open your current NGINX-config file it should be located here `/etc/nginx/sites-enabled` and end with `.conf`. In this file simply add the following two locations in your server.

``` nginx
location ~* ^/avatars/[0-9a-z]+.jpeg {
    root /var/www;
}

location ~* ^/avatars/[0-9a-z]+ {
    rewrite ^(.*)$ $1.jpeg;
}
```

if you have your avatars folder in a differnt location you need to change the path of `root`. If your folder has a diffrent name you need to adjust both urls to match the name of your folder. 
Restart nginx
```bash
sudo systemctl restart nginx
```

Now you can try your setup, take the email-address of a user that has a thumbnail set and hash it with md5 (for example [here](https://www.md5hashgenerator.com/)) (you need to make the email all lower case) open a web browser and open this domain `http://<your-server-name>/avatars/<the-hash>` you should see the Thumbnail Picture of the user you have chosen.

To execute this script periodically you need to create a CronJob opening crontab by executing the following command

```bash
crontab -e
```

Now add at the end of the file the following lines:

```
0 1 * * * python3 /opt/AD-gravatar-bridge/ad-gravatar-bridge.py
```

This will execute the script every day at 1:00 AM. You can adjust this by changing the first five values, have a look ath this [page](https://crontab.guru/). You maybe need to edit the path to the python script.

## Integration with Jitsi-meet

I created this script so that users in Jitsi-meet get their corresponding image when they dont have their webcam enabled. to achive this you need to install the script as mentioned in the install section. You don't need to install NGINX because it should be already there, just edit the`your-domain.conf` file in `/etc/nginx/sites-enabled/`. Put the two location in the second server section (the one with `listen 443 ssl;` at the top). You have to put it as the first location there so over:

```nginx
location = /config.js {
    alias /etc/jitsi/meet/example.com-config.js;
}
location = /external_api.js {
    alias /usr/share/jitsi-meet/libs/external_api.min.js;
}
```

Then you have to open this file: `/etc/jitsi/meet/example.com-config.js`. uncomment the following line and set it to your domain:

```javascript
    // Base URL for a Gravatar-compatible service. Defaults to libravatar.
    gravatarBaseURL: 'https://example.com/avatars/',
```

