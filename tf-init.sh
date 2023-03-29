set -e

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $BASEDIR/inc.sh

header "Terraform Init"

cd $BASEDIR/../terraform

terraform init \
    -backend-config="bucket=${TERRAFORM_BACKEND_S3_BUCKET}" \
    -backend-config="region=ap-southeast-2" \
    -backend-config="key=${TERRAFORM_BACKEND_KEY}" \
    -backend-config="dynamodb_table=${TERRAFORM_BACKEND_DDB_TABLE}"
