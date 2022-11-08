import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import base64

key = "Vehicle"

client = boto3.client(
    "lex-runtime",
    aws_access_key_id="AKIAVQLFYJWZOLGIJEHR",
    aws_secret_access_key="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",
)

s3client = boto3.client('s3')

host = 'search-photos-kglyeztx7h7vslcgxqektg5xoa.us-east-1.es.amazonaws.com'
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)


def get_key():
    return key


def lambda_handler(event, context):
    ambiguous_kw = get_key()
    # need to send message to aws lex

    lex_response = client.post_text(
        botName="photobot",
        botAlias="beta",
        userId="378707398066",
        inputText=ambiguous_kw,
    )
    
    # lex_message = lex_response["message"]
    lex_message = lex_response["slots"]["keywords"]
    print(lex_message)
    
    opensearch_client = OpenSearch(
        hosts = [{'host': host, 'port': 443, 'method': 'GET'}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    query = {
        "size": 3000,
        "query": {
            "multi_match": {
                "query": lex_message,
                'fields': ['labels']
            }
        }
    }
    
    openSearch_response = opensearch_client.search(
        body=query,
        index='photos'
    )
    
    for hit in openSearch_response['hits']['hits']:
        bucket_name = hit['_source']['bucket']
        photo_name = hit['_source']['objectKey'] 
        s3client_response = s3client.get_object(Bucket=bucket_name, Key=photo_name)
        image = s3client_response['Body'].read() 
        return {
            'headers': { "Content-Type": "image/png" },
            'statusCode': 200,
            'body': base64.b64encode(image).decode('utf-8'),
            'isBase64Encoded': True
        }  
    
     