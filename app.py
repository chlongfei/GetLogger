"""Simple message receiving api for collecting categorized messages
Not intended for high performance but mearly to accomplish a simple usage requirement.
Not rigorously tested for stabiilty, don't hit to too hard.

**Security**
This utilizes basic authentication to detern honest unauthorized persons from access, don't store sensitive
information on this application, the authentication is just for show.

**HTTPS**
Utilize HTTPS, even better yet, use a reverse proxy when hosting this.

lchen@chlf.dev
April 2024

THIS PROGRAM IS PROVIDED AS-IS WITHOUT WARRANTIES AND/OR SUPPORT.
"""
import os, json, datetime, sys, atexit
from dotenv import load_dotenv
from flask import Flask, request, Response, render_template
from flask_httpauth import HTTPBasicAuth

myPid = os.getpid()

app = Flask(__name__)
auth = HTTPBasicAuth()
load_dotenv()


## Basic Authentication ##
authUsers = {
    os.getenv("WEB_ADMIN_USR") : os.getenv("WEB_ADMIN_PWD")
}

@auth.verify_password
def authenticate(uname, passwd):
    try:
        if (len(os.getenv("WEB_ADMIN_IP"))):
            assert (request.remote_addr == os.getenv("WEB_ADMIN_IP"))
        assert (os.getenv("WEB_ADMIN_USR") == uname)
        assert (os.getenv("WEB_ADMIN_PWD") == passwd)
        return os.getenv("WEB_ADMIN_USR")
    except AssertionError:
        print("WARN: Unauthorized access attempted from " + request.remote_addr, file=sys.stderr)
        return False

## Load Campaigns ##
with open(os.getenv("CAMPAIGN_FILE")) as campaignFile:
    campaignList = json.loads(campaignFile.read())

## Create Campaign Log Files (if not exist) ##
for camp in campaignList:
    directory = os.getenv("FILES_DIR") + '/' + camp
    with open(directory,'a') as blah:
        pass

## Functions ##
def isCampaignExist(campaignName):
    assert (campaignList.get(campaignName) != None)

def isCampaignActive(campaignName):
    assert (campaignList.get(campaignName).get("active"))

def isCampaignKey(campaignName, campaignKey):
    assert (campaignList.get(campaignName).get("key") == campaignKey)

def writeMessage(campaignName, senderFrom, body):
    with open(os.getenv("FILES_DIR") + "/" + campaignName, "a+") as fd:
        fd.write(str(datetime.datetime.now()) + ", " + senderFrom + ", " + body + "\n")

## Get mailbox files ##
def getMailboxes():
    html = ""
    for mb in os.listdir(os.getenv("FILES_DIR")):
        html += "<div><a href=\"mailbox/get/{mbx}\">{mbx}</a></div>".format(mbx=mb)

    return html

## APIs ##
@app.route('/')
def henlo():
    """henlo am alive
    """
    return 'OK', 200

@app.route('/tell/<campaign>/<campaignKey>/<senderFrom>/<body>')
def logMessage(campaign, campaignKey, senderFrom, body):
    """Appends message log belonging to campaign
    Args:
        campaign: name of the campaign to log message under
        campaignKey: secret complex identifier serving as a password
        senderFrom: string name provided to identify message origin
        body: message body
    """
    try:
        isCampaignExist(campaign)
        isCampaignActive(campaign)
        isCampaignKey(campaign,campaignKey)
        writeMessage(campaign, senderFrom, body)
        return 'OK', 200
    except AssertionError:
        return "BAD REQUEST", 400
    

## UI - mailbox ## 
@app.route('/mailbox')
@auth.login_required
def mailbox():
    """Presents list of links to view each campaign
    """
    mailboxBtns = os.listdir(os.getenv("FILES_DIR"))
    return render_template("mb.html", mailboxes=mailboxBtns)

@app.route('/mailbox/get/raw/<campaignName>')
@auth.login_required
def getMailbox(campaignName):
    """Serves campaign messages in plain text
    Args:
        campaignName: name of the campaign to log message under
    """
    with open(os.getenv("FILES_DIR") + "/" + campaignName, "r") as fd:
        res = Response(
            response=fd.read(),
            status=200,
            mimetype="text/plain"
        )    
        return res
    
@app.route('/mailbox/get/<campaignName>')
@auth.login_required
def getView(campaignName):
    """Presents contents of each campaign to client
    Args:
        campaignName: name of the campaign to log message under
    """
    with open(os.getenv("FILES_DIR") + "/" + campaignName, "r") as fd:
        msgList = fd.read().split('\n')
        messages = list()
        for msg in msgList:
            messages.append(msg.split(','))

        return render_template("view.html",
                               campaignName=campaignName,
                               messages=messages)


## UI - Configuration - Campaigns ##
@app.route('/config/campaign')
@auth.login_required
def getCampaignJson():
    """Serves page to allow editing of CAMPAIGN_FILE
    """
    with open(os.getenv("CAMPAIGN_FILE"), "r") as fd:
        conf = fd.read()
        return render_template("conf-campaigns.html", conf=conf)

@app.route('/config/campaign/set', methods=['POST'])
@auth.login_required
def setCampaignJson():
    """Accepts new campaign JSON file and restarts application
    """
    data = request.get_json()

    # update the campaign file
    with open(os.getenv("CAMPAIGN_FILE"), "w") as fd:
        fd.write(json.dumps(data))
    # commit suicide but not before calling self start
    print("INFO: Server updating CAMPAIGN_FILE, collected own pid="+str(myPid)+" ,good bye.", file=sys.stderr)
    os.system("/bin/bash -c \"kill -s SIGTERM "+str(myPid)+"; python app.py\"")
    return 'OK', 200


## UI - Misc ##
@app.route('/service-check')
@auth.login_required
def getServiceCheck():
    """Serves a page that just waits for server to be alive again
        pinging the root api until it works.
    """
  
    return render_template("service-check.html")


## SERVE FLASK ##
if __name__ == '__main__':

    from waitress import serve
    print("INFO: Server now listening at " + os.getenv("WEB_LISTEN_ON") + ":" + os.getenv("WEB_LISTEN_AT"), file=sys.stderr)
    serve(app,host=os.getenv("WEB_LISTEN_ON"),port=os.getenv("WEB_LISTEN_AT"))