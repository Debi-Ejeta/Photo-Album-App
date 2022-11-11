import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import base64
import os

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
    hosts=[{'host': host, 'port': 443, 'method': 'GET'}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

def clean_dict(dict_obj):
    """
    This function removes duplicated values from the dictionary
    """
    temp = {val: key for key, val in dict_obj.items()}
    return {val: key for key, val in temp.items()}

def lambda_handler(event, context):
    lex_message = ""
    count = 0
    images_obj = {}  # empty object that will store images
    photo_label = []
    ambiguous_kw = event['queryStringParameters']['q']
    lex_response = client.post_text(
        botName="photobot",
        botAlias="beta",
        userId="378707398066",
        inputText=ambiguous_kw,
    )
    

    try:
        kw1 = lex_response["slots"]["keyone"]
        kw2 = lex_response["slots"]["keytwo"]

        if not kw2:
            lex_message = kw1
        else:
            lex_message = kw1 + " " + kw2

    except KeyError:
        lex_message = ""  # lex could not disambiguate the query

    query = {
        "size": 3000,
        "query": {
            "match": {
                "labels": lex_message
            }
        }
    }


    """
    query = {
        "size": 3000,
        "query": {
            "multi_match": {
                "query": lex_message,
                'fields': ['labels']
            }
        }
    }
    """

    openSearch_response = opensearch_client.search(
        body=query,
        index='photos'
    )

    for hit in openSearch_response['hits']['hits']:
        bucket_name = hit['_source']['bucket']
        photo_name = hit['_source']['objectKey']
        photo_label = hit['_source']['labels']
        images_obj[count] = os.path.join("https://", bucket_name + ".s3.amazonaws.com", photo_name)
        count += 1

    return {
        'statusCode': 200,
        'headers': {
            "Content-Type":"application/json",
            "Access-Control-Allow-Origin":"*"
        },
        'body': json.dumps({
            "results": [
                {
                    "url": clean_dict(images_obj),
                    "labels": photo_label
                }
            ]
        })
    }

