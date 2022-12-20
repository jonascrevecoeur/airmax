$artifact="openaq-realtime-analysis-flink.zip" 
$awsbucket="deployment-artifacts-jonas"
$application_name="openaq-realtime-aggregation-jonas"

## Create deployment artifacts
if(Test-Path -Path artifacts/$artifact -PathType Leaf) {
    rm "artifacts/$artifact"
} 

zip -r artifacts/$artifact lib/*
zip -r artifacts/$artifact compute-realtime-air-quality.py

aws s3api put-object --bucket deployment-artifacts-jonas --key $artifact --body artifacts/$artifact

## Update the application
$current_version=$(aws kinesisanalyticsv2 describe-application --application-name $application_name --query ApplicationDetail.ApplicationVersionId)

aws kinesisanalyticsv2 update-application `
    --application-name $application_name `
    --current-application-version-id $current_version `
    --application-configuration-update file://application-update.json

    