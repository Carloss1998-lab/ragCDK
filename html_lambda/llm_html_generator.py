import json
import re
import os
from os import getenv

env = os.environ.get('ENVIRONMENT', 'dev')
html_header = os.environ.get('LLM_MODEL_NAME', 'Llama2-7B')

def handler(event, context):
    # TODO implement
    print(event)
    print(context)
    runtime_region = os.environ['AWS_REGION']
    htmlFile = open('content/rag_llm.html', 'r')

    apiGatewayUrl = 'https://' + event['requestContext']['apiId'] + '.execute-api.' + runtime_region + '.amazonaws.com' + event['requestContext']['path']
     
    print("apiGatewayUrl")
    print(apiGatewayUrl)
    #Read contents of sample html file
    htmlContent = htmlFile.read()
    htmlContent = re.sub('<apiGatewayUrl>', apiGatewayUrl, htmlContent)
    htmlContent = re.sub('<htmlheader>', html_header, htmlContent)
    return {
        'statusCode': 200,
        'headers': {"Content-Type":"text/html"},
        'body':htmlContent
    }
