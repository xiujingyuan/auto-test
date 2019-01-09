#!/usr/bin/env python
import os
import shutil

from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.common.config.config import config

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

base_dir = os.path.abspath(os.path.dirname(__file__))
base_config_url = os.path.join(base_dir, "environment")
dev_config_url = os.path.join(base_config_url, "dev", "config.py")
test_config_url = os.path.join(base_config_url, "test", "config.py")
prod_config_url = os.path.join(base_config_url, "prod", "config.py")
dst_config_url = os.path.join(base_dir, "app", "common", "config", "config.py")



@manager.command
def init():
    input_init_str = "Please select the environment you want to init:\r\n"
    aevalible_index_dict = {}
    for index, env in enumerate(list(config.keys())[:-1]):
        input_init_str += "{0}:{1}\r\n".format(index+1, env)
        aevalible_index_dict[str(index+1)] = env

    while True:
        select_env = input(input_init_str)
        if select_env in list(aevalible_index_dict.keys()):
            break
    print(select_env)
    select_env = int(select_env)
    while True:
        input_over_str = "Do you over the config?|Yes|No"
        select_str = input(input_over_str)
        if select_str.lower() == "yes":
            src = dev_config_url
            if select_env == 2:
                src = test_config_url
            elif select_env == 3:
                src = prod_config_url
            dst = dst_config_url
            shutil.copyfile(src, dst)
            print("Over file success!")
            break
        elif select_str.lower() == "no":
            break


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade

    # migrate database to latest revision
    upgrade()


if __name__ == '__main__':
    manager.run()
