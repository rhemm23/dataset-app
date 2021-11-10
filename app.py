import flask

app = flask.Flask(__name__)

# API routes
import api

# Dynamic content
import dyn

# Import main routes
import routes

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000)

