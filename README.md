# GetLogger
Simple message receiver via HTTP GET.

## Warnings
This program is not secure by design, authenticated areas are protected by bare minimum simple HTTP Basic Authentication which is **Not Secure**.

Do not emit any sensitive information across to this server.

The program's purpose is to act as a point for where automated systems/scripts can emit a 'ping' indicating an event.

`Practice safe networking.`

## API
### `GET /`
is alive check

### `GET /mailbox`
> 🔒 is authenticated

presents a list of campaigns viewable

### `GET /mailbox/get/<campaignName>`
> 🔒 is authenticated

dumps the contents of the campaign log file to client to view in CSV format.

client can choose to Save-As page to download.

### `GET /tell/<campaign>/<campaignKey>/<senderFrom>/<body>`
accepts messages with valid campaign and campaignKey combination logging to respective campaign files.

## Campaigns
Campaigns are defined in the `campaigns.json` file, it is in this file that the campaign name, key, and is active is defined.

> Restart server after modifying this file to apply changes.

### Sample Campaign config
```json
{
    "campaignName":{
        "key":"somethingComplexButHTMLFriendly",
        "active":true
    }   
}
```

## Server Configuration
Application parameters are set in the `.env` file.

> leave `WEB_ADMIN_IP` empty to disable IP based ACL

### Sample config
```json
WEB_LISTEN_ON="0.0.0.0"
WEB_LISTEN_AT="8080"
WEB_ADMIN_IP="192.168.192.1"
WEB_ADMIN_USR="admin"
WEB_ADMIN_PWD="admin"
FILES_DIR="datastore"
CAMPAIGN_FILE="campaigns.json"
```