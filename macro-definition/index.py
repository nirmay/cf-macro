import boto3
import yaml

def process_template(template,parameters):
    status = 'failed'
    
    bucket, key = split_s3_path(parameters['S3Location'])
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket, Key=key)

    try:
        configfile = yaml.safe_load(response["Body"])
    except yaml.YAMLError as exc:
        return status, exc
    
    for k, v in configfile.items():
        #Assume that attribute hierarchy for WriteCapacityUnits and BatchSize
        #Replace this with code that can identify the attribute hierarchy of CF attribute changed
        if str(k) == "WriteCapacityUnits":
            template['Resources']['DynamoDBTable']['Properties']['ProvisionedThroughput']['WriteCapacityUnits'] = v
        else:
            template['Resources']['ReadDynamoDBEvent']['Properties']['Events']['DynamoDBEvent']['Properties']['BatchSize'] = v
    status = 'success'        
    return status, template

def split_s3_path(s3_path):
    path_parts=s3_path.replace("s3://","").split("/")
    bucket=path_parts.pop(0)
    key="/".join(path_parts)
    return bucket, key
    
def handler(event, context):
    result = process_template(event['fragment'],event['templateParameterValues'])
    return {
        'requestId': event['requestId'],
        'status': result[0],
        'fragment': result[1],
    }
