# Copyright (c) 2020 Aldo Hoeben / fieldOfView
# CustomJobPrefix is released under the terms of the AGPLv3 or higher.

from . import CustomJobPrefix

def getMetaData():
    return {}

def register(app):
    return {"extension": CustomJobPrefix.CustomJobPrefix()}
