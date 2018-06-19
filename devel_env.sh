#!/bin/bash
export FLASK_APP=captaina
export FLASK_ENV=developement
export FLASK_DEBUG=True
export FLASK_INSTANCE_PATH="$PWD"/debug_instance
[[ -f ./.venv/bin/activate ]] && source ./.venv/bin/activate
