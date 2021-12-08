#!/usr/bin/env python
from flask_script import Manager, Server

from app import create_app
import os

app = create_app()
manager = Manager(app)
env = os.environ.get('environment', 'dev')
use_debugger = True if env == 'dev' else False
manager.add_command("runserver", Server(use_debugger=use_debugger))

if __name__ == '__main__':
    manager.run()
