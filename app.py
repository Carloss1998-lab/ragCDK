#!/usr/bin/env python3
import os
import boto3
import aws_cdk as cdk
from aws_cdk import (
    Fn
)

from mirage.mirage_stack import MirageStack
from mirage.openSearch_stack import OpenSearchStack
from mirage.ecr_stack import Ecrstack
from datetime import datetime

region_name = boto3.Session().region_name

endpoint = "MirageMistralEndpoint" # MistralGPTQ

# current_utc_timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")


MODEL_INFO = {"endpoint":endpoint,
              "account_id" : '555043101106', 
              "region" : "us-east-1",
              "collection_name": "samplevectorstoredev",
             "index_name": "sampleembeddingsdev",
             "lambda_role_name": "lambdallmragdev",
             "project_id": "mirage",
             "ecr_repository_name": "lambdaragrepodev",
             "model_path": "/var/task/sentencetransformers/", # lambdaDock\embed_model.zip contain the folder sentencetransformers
             'tag' : 'v1'}

print("MODEL_INFO")
print(MODEL_INFO)

app = cdk.App()

ops_stack = OpenSearchStack(app,f"opensearch{MODEL_INFO['project_id']}",model_info=MODEL_INFO)
MirageStack(app, "mirageMistralStack",model_info=MODEL_INFO,ops_endpoint=ops_stack.collection_endpoint)
Ecrstack(app,f"ecr{MODEL_INFO['project_id']}",model_info=MODEL_INFO)
app.synth()

# aws codebuild start-build --project-name lambdaragllmcontainermirage-HopLKwbuUIj7