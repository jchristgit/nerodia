# Nerodia
A Reddit Bot that follows Twitch streams on a per-subreddit basis
and updates the subreddit's sidebar when a followed stream goes
online or offline.

### Setup
While I recommend just using the [running version of Nerodia](https://reddit.com/u/Botyy)
instead, it is possible to run your own instance. Please only do this if you know
what you are doing and have basic programming knowledge. In order to accomplish this, you need
to perform a few configuration steps. An [example configuration file](./config-example.json)
is provided. The following section explains how to obtain the various data.

- `discord_auth | token`
You can obtain this by visiting [Discord - My Apps](https://discordapp.com/developers/applications/me),
creating a new app by clicking `New App`, and then after creating it, copying the `Token` from
`App Bot User` on the Bot page. Paste the token into the empty `""`, and the Discord Bot is set up.

- `reddit_auth`
For detailed information abotu authenticating via OAuth through PRAW, please read through
[Authenticating via OAuth from the PRAW docs](http://praw.readthedocs.io/en/latest/getting_started/authentication.html).
This should explain everything you need.
For determining a nice user agent, please read through the [Reddit API Rules](https://github.com/reddit/reddit/wiki/API#rules).

- `twitch_auth | client_id`
For obtaining a client ID for using the Twitch API, click `Register your app` on the bottom of
the [Twitch Connections page](https://www.twitch.tv/settings/connections). You can simply
copy the `Client ID` from the application you created afterwards, and paste it into the empty `""`.

That's it for the authentication part.
Now, you need to install requirements. This is as simple as running
```sh
$ pip3 install -r requirements.txt
```
After you installed the requirements, you can perform an additional configuration step
and change the environment variable `NERODIA_DB_PATH` to where ever you want the SQLite
database to house. This defaults to `./data/nerodia.db`.


### Running the tests
Integration tests are run using [tox](https://github.com/tox-dev/tox).
Install it using `pip3 install tox`, and then simply run `tox` from the
root directory of the project. The environment variable `NERODIA_DB_PATH`
will be changed to `test/test.db` to ensure that the tests do not mess up
the actual database used in the bot. You can change this by editing `tox.ini`.


### Disclaimer
Nerodia isn't endorsed by Discord, Reddit or Twitch and does not
reflect the views or opinions of Discord, Reddit or Twitch.

Nerodia stores the Discord ID of users who connected their Discord account
with their reddit account through the `connectreddit` in a SQLite database
which is not directly accessible from external sources. Users consent to this
through using the command, as it provides a disclaimer informing about this.
