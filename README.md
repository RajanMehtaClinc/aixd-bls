## Requirements
You must have Python 3.5+ to use this BLS.


# Installation
Install the dependencies:
```
make install
```

Install the dependencies including those for development:
```
make install-dev
```

## Testing
Run the tests:
```
make test
```

Get coverage report:
```
make coverage
```


## Linting
Run the linter:
```
make lint
```


# Debugging
Stand up the server in debug mode:
```
make debug
```

Now you can send POST requests locally via Postman (or cURL) given the address and port number shown on the command line in response to the previous command.

I recommend having the following environment variable for debugging:

- FLASK_ENV=development


# Deploying
For deployment, either look into [deploying a Python app on Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app) or [exposing a local server with ngrok](https://dashboard.ngrok.com/get-started).
