# screencast

_screencast_ is a two-part application for casting your desktop to a central location:

* _server.py_: waits for a URL from the _cast.py_ script and starts VLC;
* _cast.py_: runs VLC locally as a daemon and sends the URL to the server.

## Preparing

This project uses [pipenv](https://docs.pipenv.org/). 
Follow the [official documentation](https://docs.pipenv.org/install/) and install pipenv before continuing.

Both the server and client will also need to have VLC installed. Use your OS package system to install it.

## Running

### Client

To start the client, type:

    pipenv run python cast.py start

To stop the client, type:

    pipenv run python cast.py stop

### Server

TODO

