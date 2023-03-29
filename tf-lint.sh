set -e

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $BASEDIR/inc.sh

header "Terraform lint"

cd $BASEDIR/../terraform

pip install black

black --check ../src/

terraform init -backend=false

terraform validate

terraform fmt -check -diff
