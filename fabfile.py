import os

from fabric.api import env, cd, execute, roles, run, sudo


LOCAL_DIR = os.path.realpath(os.path.dirname(__file__))
PROD_DIR = '/home/cabbie/workspace/cabbie-backend'
ACTIVATE = '/home/cabbie/.virtualenvs/cabbie/bin/activate'

env.roledefs = {
    'prod': ['bktaxi.com'],
}
env.user = 'cabbie'
env.password = 'roqkfwk1'

def prepare():
    with cd(LOCAL_DIR):
        pass

@roles('prod')
def deploy_web():
    with cd(PROD_DIR):
        run('git pull origin master')
        sudo('supervisorctl restart cabbie-web')

@roles('prod')
def deploy_celery():
    with cd(PROD_DIR):
        run('git pull origin master')
        sudo('supervisorctl restart cabbie-celery')
        sudo('supervisorctl restart cabbie-celerybeat')

@roles('prod')
def deploy_location():
    with cd(PROD_DIR):
        run('git pull origin master')
        sudo('supervisorctl restart cabbie-location')

def deploy():
    prepare()
    execute(deploy_web)
    execute(deploy_celery)
    execute(deploy_location)
