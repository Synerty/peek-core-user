#!/bin/bash

set -o nounset
set -o errexit
set -x

PLUGIN_NAME="plugin_userdb"

# activate virtualenv
export PATH=/home/bamboo/pyenvs/py_ut/bin:$PATH

# Define python path
PYTHONPATH="`pwd`/peek_plugin/src"
PYTHONPATH="$PYTHONPATH:`pwd`/rapui/src"
PYTHONPATH="$PYTHONPATH:`pwd`/${PLUGIN_NAME}/src"
export PYTHONPATH


FILES=`find $PLUGIN_NAME -name "*.py" -exec grep -l unittest.TestCase {} \;`
echo "Running unit tests in files:"
echo $FILES

JUNIT_DIR=.junit
mkdir ${JUNIT_DIR}
OUT=${JUNIT_DIR}/trial.xml

# Trial exists non-zero if there are failed tests, we want to ignore this
trial --reporter=subunit ${FILES} | subunit-1to2 | subunit2junitxml -o $OUT || true

echo "Finished"


