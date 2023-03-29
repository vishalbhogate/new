set -e

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $BASEDIR/inc.sh

header "Terraform Apply"

cd $BASEDIR/../terraform

terraform apply ../artifacts/tfplan-"$STAGE"
