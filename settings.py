# A lib to check if certain settings are enabled for servers. Will be used to disable and enable features on a per-server basis
import os
import math
import json
filepath = os.path.abspath(os.path.dirname(__file__))


def check(serverid, action="get", setting=None, val=None):
    if os.path.isfile(filepath + "/settings/" + str(serverid) + ".json"):
        with open(filepath + "/settings/" + str(serverid) + ".json", "r") as f:
            with open(filepath + "/settings/" + str(serverid) + ".json", "w") as r:
                try:
                    settings = json.load(f)
                except json.decoder.JSONDecodeError:
                    settings = {}
                if action == "get":
                    if setting is None:
                        return settings
                    elif setting in settings:
                        return settings[setting]
                    else:
                        return True
                elif action == "set":
                    if setting is None:
                        return False
                    elif val is None:
                        return False
                    else:
                        settings[setting] = val
                        r.write(json.dumps(settings))
                        return True
    else:
        if action == "get":
            settings = {}
            settings[setting] = True
            f = open(filepath + "/settings/" +
                     str(serverid) + ".json", "w")
            f.write(json.dumps(settings))

            return True
        elif action == "set":
            if setting is None:
                return False
            elif val is None:
                return False
            else:
                settings = {}
                settings[setting] = val
                f = open(filepath + "/settings/" +
                         str(serverid) + ".json", "w")
                f.write(json.dumps(settings))

                return True
