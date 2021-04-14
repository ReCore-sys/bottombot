# A lib to check if certain settings are enabled for servers. Will be used to disable and enable features on a per-server basis
import os
import math
import json
filepath = os.path.abspath(os.path.dirname(__file__))


def check(serverid, action="get", setting=None, val=None):
    try:
        f = open(f"{filepath}/serversettings/{serverid}/settings.json", "r")
        v = json.loads(f.read())
        f.close()
        if action == "get":
            try:
                return v[setting]
            except:
                return None
        elif action == "set":
            v[setting] = val
        f = open(f"{filepath}/serversettings/{serverid}/settings.json", "w")
        f.write(json.dumps(v))
        f.close()
    except:
        return True
