import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import base64
import os

key = "vehicle"

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

opensearch_client = OpenSearch(
    hosts = [{'host': host, 'port': 443, 'method': 'GET'}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)


def get_key():
    return key
    
def clean_dict(dict_obj):
    """
    This function removes duplicated values from the dictionary
    """
    temp = {val : key for key, val in dict_obj.items()}
    return {val : key for key, val in temp.items()}
        

def lambda_handler(event, context):
    return json.dumps(event['queryStringParameters'])
    count = 0
    images_obj = {} # empty object that will store images
    ambiguous_kw = get_key()
    lex_response = client.post_text(
        botName="photobot",
        botAlias="beta",
        userId="378707398066",
        inputText=ambiguous_kw,
    )

    
    try:
        kw = lex_response["slots"]["keywords"]
        kw_li = kw.split(" ")
        # lex_message = " and ".join(kw_li)
        lex_message=kw
        
    except KeyError:
        lex_message = "" # lex could not disambiguate the query
    
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
        images_obj[count] = os.path.join("https://", bucket_name + ".s3.amazonaws.com", photo_name)
        count += 1
    
    return {
        'statusCode': 200,
        'body': clean_dict(images_obj)
    }
    
