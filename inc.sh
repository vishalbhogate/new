function log() {
    echo "- $1"
}
function header() {
    echo '---------------------------------'
    echo $1
    echo '---------------------------------'
}
echo "Code Branch: ${CI_COMMIT_BRANCH}"

if [[ ${CI_COMMIT_BRANCH} == "develop" ]]
then
    STAGE="non-prod"
elif [[ ${CI_COMMIT_BRANCH} == "main" ]]
then
    STAGE="prod"
else
    STAGE="sandbox"
fi
echo "Stage: $STAGE"
