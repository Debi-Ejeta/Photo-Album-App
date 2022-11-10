import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

host = 'search-photos-kglyeztx7h7vslcgxqektg5xoa.us-east-1.es.amazonaws.com'
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    photo_name = event['Records'][0]['s3']['object']['key']
    print(bucket_name)
    print(photo_name)
    client=boto3.client('rekognition', 'us-east-1')
    rekogniton_resp = client.detect_labels(Image={'S3Object':{'Bucket':bucket_name,'Name':photo_name}},
        MaxLabels=10)
    labels = []
    for label in rekogniton_resp['Labels']:
        labels.append(label['Name'])
        
    s3client = boto3.client('s3')
    s3client_resp = s3client.head_object(Bucket=bucket_name, Key=photo_name)
    # metadata = s3client_resp['Metadata']
    # Need to figure out why metadata is empty and how to add it
    # print(s3client_resp)

    custom_labels = s3client_resp['Metadata']['customlabels'].split(",")
    labels = labels + custom_labels
    
    image_timestamp = s3client_resp['LastModified']
    document = {
        "objectKey": photo_name,
        "bucket": bucket_name,
        "createdTimestamp": image_timestamp,
        "labels": labels
    }
    
    opensearch_client = OpenSearch(
        hosts = [{'host': host, 'port': 443, 'method': 'PUT'}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    #opensearch_client.indices.create("photos")
    res = opensearch_client.index(index="photos", body=document)
    
    print(res)
    
    
    
    
    
