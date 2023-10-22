import os
from aws_cdk import (
    Stack,
    CfnTag,
    aws_opensearchserverless as _oss,
    Tag as _tags,
    CfnOutput as _output
)
from constructs import Construct
import os

class OpenSearchStack(Stack):

    def __init__(self, scope: Construct, id: str,model_info,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        project_id = model_info["project_id"]
        account_id = model_info["account_id"]
        collection_name = model_info['collection_name']
        index_name = model_info['index_name']

        lambda_role_arn = f"arn:aws:iam::{account_id}:role/{model_info['lambda_role_name']}"
        encryption_policy = _oss.CfnSecurityPolicy(self, f'samplevectordbencrypt{project_id}',  name=f'samplevectordbencryption{project_id}',
                                type='encryption',
                                policy="""{\"Rules\":[{\"ResourceType\":\"collection\",\"Resource\":[\"collection/"""+ collection_name +"""\"]}],\"AWSOwnedKey\":true}""")
        
        network_policy = _oss.CfnSecurityPolicy(self, f'samplevectordbnw{project_id}', 
                                                name=f'samplenectordbnw{project_id}',
                                type='network',
                                policy="""[{\"Rules\":[{\"ResourceType\":\"collection\",\"Resource\":[\"collection/"""+ collection_name + """\"]}, {\"ResourceType\":\"dashboard\",\"Resource\":[\"collection/"""+ collection_name + """\"]}],\"AllowFromPublic\":true}]""")
        
        data_access_policy = _oss.CfnAccessPolicy(self, f'samplevectordbdata{project_id}', name=f'samplevectordbdata{project_id}',
                                type='data',
                                policy="""[{\"Rules\":[{\"ResourceType\":\"index\",\"Resource\":[\"index/"""+ collection_name +"""/*\"], \"Permission\": [\"aoss:*\"]}, {\"ResourceType\":\"collection\",\"Resource\":[\"collection/"""+ collection_name +"""\"], \"Permission\": [\"aoss:*\"]}], \"Principal\": [\"""" + lambda_role_arn + """\"]}]""")

        #have to create  security policy before creating new collection  
        cfn_collection = _oss.CfnCollection(self, f"vectordbcollection{project_id}",
            name=collection_name,
            # the properties below are optional,
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            description="Serverless vector db example",
            type="VECTORSEARCH"
        )

        
        cfn_collection.add_dependency(encryption_policy)
        cfn_collection.add_dependency(network_policy)
        cfn_collection.add_dependency(data_access_policy)
        
        _output(self, f'collection_endpoint_{project_id}',
                value=cfn_collection.attr_collection_endpoint,
                description='Collection Endpoint',
                export_name='collectionEndpointUrl'
                )
        self.collection_endpoint = cfn_collection.attr_collection_endpoint
