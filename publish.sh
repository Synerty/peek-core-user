#!/usr/bin/env bash

PY_PACKAGE="peek_core_user"
PIP_PACKAGE="peek-core-user"

set -o nounset
set -o errexit
#set -x

if [ -n "$(git status --porcelain)" ]; then
    echo "There are uncommitted changes, please make sure all changes are committed" >&2
    exit 1
fi

if ! [ -f "setup.py" ]; then
    echo "setver.sh must be run in the directory where setup.py is" >&2
    exit 1
fi

VER="${1:?You must pass a version of the format 0.0.0 as the only argument}"

if git tag | grep -q "${VER}"; then
    echo "Git tag for version ${VER} already exists." >&2
    exit 1
fi

echo "Setting version to $VER"

# Update the setup.py
sed -i "s;^package_version.*=.*;package_version = '${VER}';"  setup.py

# Update the package version
sed -i "s;.*version.*;__version__ = '${VER}';" ${PY_PACKAGE}/__init__.py

# Update the plugin_package.json
# "version": "#PLUGIN_VER#",
sed -i 's;.*"version".*:.*".*;    "version":"'${VER}'",;' ${PY_PACKAGE}/plugin_package.json

## Build the source dist package
# TODO: This should be a binary dist
python setup.py  sdist --format=gztar

# Reset the commit, we don't want versions in the commit
git commit -a -m "Updated to version ${VER}"

git tag ${VER}
git push
git push --tags

RELEASE_DIR=${RELEASE_DIR-/media/psf/release}
if [ -d  $RELEASE_DIR ]; then
    rm -rf $RELEASE_DIR/${PIP_PACKAGE}*.gz || true
    cp ./dist/${PIP_PACKAGE}-$VER.tar.gz $RELEASE_DIR
fi

#echo "If you're ha