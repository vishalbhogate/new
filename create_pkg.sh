#!/bin/bash
set -e

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $BASEDIR/inc.sh

header "Creating Package"
BASEDIR="$(dirname $BASEDIR)"

echo $BASEDIR
cd $BASEDIR
pkg_folder=artifacts/lambda_dist_pkg
mkdir -p $pkg_folder
mkdir -p artifacts/lambda_layer
cd $pkg_folder

# Install virtualenv
pip install virtualenv

# Create and activate virtual environment...
virtualenv -p $runtime env_$layer_name
source $BASEDIR/$pkg_folder/env_$layer_name/bin/activate

# Installing python dependencies...
FILE=$BASEDIR/src/requirements.txt

if [ -f "$FILE" ]; then
  echo "Installing dependencies..."
  echo "From: requirement.txt file exists..."
  pip install -r "$FILE"

else
  echo "Error: requirements.txt does not exist!"
fi

# Deactivate virtual environment...
deactivate

# Create deployment package...
echo "Creating deployment package..."
cd env_$layer_name/lib/$runtime/site-packages/
rm -rf ./__pycache__
# zip -r ../../../../my-deployment-package.zip .
cp -r . $BASEDIR/artifacts/lambda_layer/python/

# Removing virtual environment folder...
echo "Removing virtual environment folder..."
rm -rf $BASEDIR/$pkg_folder

echo "Finished script execution!"
