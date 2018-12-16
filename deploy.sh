#!/bin/bash

# dev: ./deploy.sh
# prod: ./deploy.sh prod
STAGE=${1:-dev}

PROJECT=sbaapi-$STAGE
BUCKET=$PROJECT-12152018

make

# make a build directory to store artifacts
rm -rf build
mkdir build

# make the deployment bucket in s3 if it does not exist
aws s3 mb s3://$BUCKET
if [[ $? != 0 ]]
then
    echo "FAILED WHEN CREATING AN S3 BUCKET"
    exit 1
fi

# generate next stage yaml file
aws cloudformation package \
    --template-file template.yaml \
    --output-template-file build/output.yaml \
    --s3-bucket $BUCKET
if [[ $? != 0 ]]
then
    echo "FAILED DURING YAML GENERATION"
    exit 1
fi

# the actual deployment step
aws cloudformation deploy \
    --template-file build/output.yaml \
    --stack-name $PROJECT \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides ENVIRONMENT=$STAGE
if [[ $? != 0 ]]
then
    echo "FAILED DURING CLOUDFORMATION DEPLOYMENT"
    exit 1
fi

exit 0