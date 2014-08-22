# Cabbie

## Prerequisites

- python (>=2.7)
- pip
- git


## Installation

To set up a virtual environment, run following commands in order:

```bash
sudo pip install virtualenv
sudo pip install virtualenvwrapper

export WORKON_HOME=$HOME/.virtualenvs

# /usr/bin/ or /usr/local/bin/ depending on the system
source /usr/bin/virtualenvwrapper.sh

mkvirtualenv --distribute --no-site-package cabbie

pip install -r requirements.txt
```


To compile SASS:

```bash
gem install sass
gem install compass
sass --watch cabbie/static/sass/:cabbie/static/css/ --compass
```


To create a local development environment:

```bash
cp cabbie/local_settings.py.template cabbie/local_settings.py
```


To create a local testing environment with Ionic:

```bash
cd ionic/cabbie-driver # or ionic/cabbie-passenger
npm install
ionic serve
gulp watch
```


## Todo

- Add `is_accepted` field to the `Driver` model
- Dispatch estimate information to passenger and driver
- Permission control for REST API
