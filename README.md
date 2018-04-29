[![Build Status](https://travis-ci.org/Volcyy/nerodia.svg?branch=master)](https://travis-ci.org/Volcyy/nerodia)
# Nerodia
Nerodia is an application that checks Twitch streams for updates and
notifies about this users on selected integrations.

## Setup
To install requirements, use 
```sh
$ pipenv install
```
From here on, run the commands either in `pipenv shell` or
prefix them with `pipenv run`, so they run in the virtual environment.
You now need to run the migrations with `alembic`. Use
```sh
$ alembic upgrade heads
```
to run all migrations on the database. The database used defaults
to a SQLite database at `data/nerodia.db`, but this can be set
using the `NERODIA_DB_PATH` environment variable.

Configure nerodia as you wish through `config-example.yml` by copying
it to `config.yml` and setting it up as instructed by the comments.

Finally, to run nerodia, use
```sh
python -m nerodia
```

### Disclaimer
Nerodia isn't endorsed by Discord, Reddit or Twitch and does not
reflect the views or opinions of Discord, Reddit or Twitch.
