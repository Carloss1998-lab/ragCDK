from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_ecr as _ecr,
    # aws_sqs as sqs,
)
from constructs import Construct
import aws_cdk.aws_iam as iam
from aws_cdk.aws_lambda import Function, Code, Runtime
import   aws_cdk.aws_apigateway as apigw
import os
import json

class MirageStack(Stack):

    def __init__(self, scope: Construct, id: str,model_info,ops_endpoint,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        project_id = model_info["project_id"]
        current_timestamp = model_info['tag']
        account_id = model_info["account_id"]
        region =  model_info["region"]


        collection_endpoint = ops_endpoint
        
        print("collection_endpoint")
        print(collection_endpoint)

        try:
            collection_endpoint = collection_endpoint.replace("https://", "")
        except Exception as e:
            pass
        
        print("AAA  collection_endpoint")
        print(collection_endpoint)

        # Define RAG API
        rag_llm_root_api = apigw.RestApi(
            self,
            f"rag-llm-api-{project_id}",
            deploy=True,
            deploy_options={
                "stage_name": project_id,
                "throttling_rate_limit": 100,
                "description": project_id + " stage deployment",
            },
            description="RAG with Opensearch Serverless",
        )
        rag_llm_api = rag_llm_root_api.root.add_resource("rag")

        custom_lambda_role = iam.Role(self, f'llm_rag_role_{project_id}', 
                    role_name= model_info['lambda_role_name'],
                    assumed_by= iam.ServicePrincipal('lambda.amazonaws.com'),
                    managed_policies= [
                        iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
                    ]
                )

        method_responses = [
            # Successful response from the integration
            {
                "statusCode": "200",
                # Define what parameters are allowed or not
                "responseParameters": {
                    "method.response.header.Content-Type": True,
                    "method.response.header.Access-Control-Allow-Origin": True,
                    "method.response.header.Access-Control-Allow-Credentials": True,
                },
            }
        ]

        lambda_function = _lambda.DockerImageFunction(
            self,
            f"llm_rag_{project_id}",
            description="lambda for rag api",
            function_name=f"llm_rag_example_dev",
            memory_size=1024,
            timeout=Duration.minutes(10),
            role=custom_lambda_role,
            code=_lambda.DockerImageCode.from_ecr(
                repository=_ecr.Repository.from_repository_name(
                    self,
                    f"lambda_rag_{project_id}",
                    model_info["ecr_repository_name"],
                ),
                tag_or_digest=str(current_timestamp)
            ),
            environment={   
                        'INDEX_NAME': model_info['index_name'],
                        'OPENSEARCH_ENDPOINT': collection_endpoint,
                        'MODEL_PATH': model_info['model_path'],
                        'REGION': region,
                        'MAX_TOKENS': "2000",
                        'TEMPERATURE': "0.9",
                        'TOP_P': "0.6",
                            # 'SAGEMAKER_ENDPOINT': sagemaker_endpoint_name
                    }
        )
        html_header_name = 'Llama2-7B'
        html_generation_function = Function(self, f'llm_html_function_{project_id}',
                                            function_name=f'llm-html-generator-{project_id}',
                                            runtime= Runtime.PYTHON_3_9,
                                            memory_size=128,
                                            handler='llm_html_generator.handler',
                                            timeout=Duration.minutes(1),
                                            code=Code.from_asset(os.path.join(os.getcwd(), 'html_lambda')),
                                            environment={ 'ENVIRONMENT': project_id,
                                                          'LLM_MODEL_NAME': html_header_name,
                                                        })       
        
        oss_policy = iam.PolicyStatement(
            actions=[
                "aoss:*",
                "sagemaker:*",
                "iam:ListUsers",
                "iam:ListRoles",
                "apigateway:*"
            ],
            resources=["*"],
        )

        lambda_function.add_to_role_policy(oss_policy)
        
        lambda_integration = apigw.LambdaIntegration(
            lambda_function, proxy=True, allow_test_invoke=True
        )

        html_generation_lambda_integration = apigw.LambdaIntegration(
            html_generation_function, proxy=True, allow_test_invoke=True
        )

        rag_llm_api.add_method("GET",
                                html_generation_lambda_integration, operation_name="HTML file",
                                method_responses=method_responses)
        
        query_api = rag_llm_api.add_resource("query")
        index_docs_api = rag_llm_api.add_resource("index-documents")
        index_sample_data_api = rag_llm_api.add_resource("index-sample-data")
        
        query_api.add_method(
            "GET",
            lambda_integration,
            operation_name="Query LLM with Augmented Enriched Prompt",
            method_responses=method_responses,
        )

        index_docs_api.add_method(
            "POST",
            lambda_integration,
            operation_name="index document",
            method_responses=method_responses,
        )

        index_docs_api.add_method(
            "DELETE",
            lambda_integration,
            operation_name="delete document index",
            method_responses=method_responses,
        )

        index_sample_data_api.add_method(
            "POST",
            lambda_integration,
            operation_name="index sample document",
            method_responses=method_responses,
        )

        self.add_cors_options(index_docs_api)
        self.add_cors_options(query_api)
        self.add_cors_options(index_sample_data_api)


        # # Crée la fonction Lambda
        # lambda_handler_path = os.path.join(os.getcwd(), "lambda")
        # lambda_function = Function(self, "LambdaFunction",
        #     runtime=Runtime.PYTHON_3_8,
        #     handler="lambda_handler.handler",
        #     timeout=Duration.seconds(180),
        #     code=Code.from_asset(lambda_handler_path),
        #     environment={
        #         "SAGEMAKER_ENDPOINT_NAME": model_info["endpoint"],
        #         "collection_endpoint" : collection_endpoint
        #     }
        # )

        # # add policy for invoking
        # lambda_function.add_to_role_policy(
        #     iam.PolicyStatement(
        #         actions=[
        #             "sagemaker:InvokeEndpoint",
        #         ],
        #         resources=["*"]
        #     )
        # )


        # # Defines an Amazon API Gateway endpoint for NLU & Text Generation service
        # gen_txt_apigw_endpoint = apigw.LambdaRestApi(
        #     self, "gen_txt_apigw_endpoint",
        #     handler=lambda_function
        # )     
        
    def add_cors_options(self, apiResource: apigw.IResource):
        apiResource.add_method(
            "OPTIONS",
            apigw.MockIntegration(
                integration_responses=[
                    {
                        "statusCode": "200",
                        "responseParameters": {
                            "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
                            "method.response.header.Access-Control-Allow-Origin": "'*'",
                            "method.response.header.Access-Control-Allow-Credentials": "'false'",
                            "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,PUT,POST,DELETE'",
                        },
                    }
                ],
                passthrough_behavior=apigw.PassthroughBehavior.NEVER,
                request_templates={"application/json": '{"statusCode": 200}'},
            ),
            method_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Headers": True,
                        "method.response.header.Access-Control-Allow-Methods": True,
                        "method.response.header.Access-Control-Allow-Credentials": True,
                        "method.response.header.Access-Control-Allow-Origin": True,
                    },
                }
            ],
    )
