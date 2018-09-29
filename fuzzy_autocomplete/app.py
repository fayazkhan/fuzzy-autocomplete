import sys

from flask import Flask, jsonify, request
import logbook

from .core import Autocompleter


logbook.StreamHandler(sys.stderr).push_application()
autocompleter = Autocompleter()
app = Flask(__name__)


@app.route('/search/')
def search():
    word = request.args.get('word')
    if not word:
        return jsonify({'data': []})
    return jsonify({'data': list(autocompleter.suggest_matches(word))})
