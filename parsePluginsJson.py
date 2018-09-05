import json
import codecs
import os

_DEBUG = False
# _DEBUG = True

# C4D can use UNC paths, but the next time they are changed within the app, they are stored as path + authoritypath
# instead, so for each UNC path there are two possible ways they may be stored as
_PLUGINPATHUNC = "//prime/public/R20/plugins"
_PLUGINPATH = "public/R20/plugins"
_PLUGINAUTHORITYPATH = "prime"

# A JSON block that contains a path definition
_NEWPATH = {
            "_0": {
                "referenceIndex": 0,
                "referenceDataType": "net.maxon.interface.url-C",
                "_scheme": "file",
                "_path": _PLUGINPATH,
                "_authority": {
                    "referenceDataType": "net.maxon.interface.url-C",
                    "_scheme": "authority",
                    "_path": _PLUGINAUTHORITYPATH,
                    "_authority": {},
                    "_data": {}
                },
                "_data": {}
            },
            "_1": True
        }

# The contents of a brand new definition file with out path already in it (by default the plugins.json file does 
# not exist until a path is manually added in the application)
_NEWFILE = {
    "identification": "plugins",
    "content": {
        "referenceDataType": "net.maxon.interface.datadictionary-C",
        "_impl": {
            "_mode": 2,
            "_data": [
                {
                    "dataType": "net.maxon.datatype.id",
                    "content": "searchPaths"
                },
                {
                    "dataType": "(net.maxon.interface.url-C,bool)",
                    "isArray": True,
                    "content": [
                        {
                            "_0": {
                                "referenceIndex": 0,
                                "referenceDataType": "net.maxon.interface.url-C",
                                "_scheme": "file",
                                "_path": "public/R20/plugins",
                                "_path": _PLUGINPATH,
                                "_authority": {
                                    "referenceDataType": "net.maxon.interface.url-C",
                                    "_scheme": "authority",
                                    "_path": _PLUGINAUTHORITYPATH,
                                    "_authority": {},
                                    "_data": {}
                                },
                                "_data": {}
                            },
                            "_1": True
                        }
                    ]
                }
            ]
        }
    }
}

def debug(msg):
    if _DEBUG:
        print(msg)

def hasPluginPath(content, pathToCheckFor):
    if "_path" in content:
        if content["_path"] == pathToCheckFor:
            return True
    return False

userAppData = os.getenv('APPDATA')
debug(userAppData)
maxon = os.path.join(userAppData, "MAXON")
debug(maxon)
if (os.path.exists(maxon)):
    # only look into R20 user folders
    userDirsR20 = [x for x in os.listdir(maxon) if str(x).lower().startswith("cinema 4d r20")]
    for userDir in userDirsR20:
        pluginsJsonPath = os.path.join(maxon, userDir, "plugins.json")
        debug(pluginsJsonPath)
        if os.path.exists(pluginsJsonPath):
            # the plugins.json file is stored as "UTF-8 with BOM", so regular open() will not open it correctly and json.load will fail
            with codecs.open(pluginsJsonPath, "r+", "utf-8-sig") as f:
                j = json.load(f)
                found_PLUGINPATH = False
                for data in j['content']['_impl']['_data']:
                    if data['dataType'] == "(net.maxon.interface.url-C,bool)":
                        for idx, content in enumerate(data['content']):
                            debug(content)
                            if hasPluginPath(content["_0"], _PLUGINPATH) or hasPluginPath(content["_0"], _PLUGINPATHUNC):
                                found_PLUGINPATH = True
                                data['content'][idx] = _NEWPATH
                                break
                        if not found_PLUGINPATH:
                            found_PLUGINPATH = True
                            data['content'].append(_NEWPATH)
                # write the changes back into the file
                if found_PLUGINPATH:
                    f.seek(0)
                    if _DEBUG:
                        print(json.dumps(j, indent=4, sort_keys=False))
                    else:
                        f.writelines(json.dumps(j, indent=4, sort_keys=False))
                        f.truncate()
        else:
            with codecs.open(pluginsJsonPath, "w+", "utf-8-sig") as f:
                f.writelines(json.dumps(_NEWFILE, indent=4, sort_keys=False))
else:
    exit