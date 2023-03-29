set -e

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "- Print out Env vars:"
echo "  + Code Branch: $CI_COMMIT_BRANCH"
echo ""

source $BASEDIR/inc.sh

header "Terraform Plan"

echo $STAGE

cd $BASEDIR/../terraform
mkdir -p artifacts

terraform plan \
    -var-file=vars/prod.tfvars \
    -out=../artifacts/tfplan-"$STAGE"
