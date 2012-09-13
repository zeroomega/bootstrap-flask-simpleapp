#!/usr/bin/env python
#Avoid Python Version Prior to required to execute this script
from __future__ import absolute_import

from flask.ext.script import Manager

from app import app


manager = Manager(app)

if __name__ == "__main__":
    manager.run()
