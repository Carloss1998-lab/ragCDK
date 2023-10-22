from aws_cdk import (
    Stack,
    aws_iam as _iam,
    aws_ecr as _ecr,
    aws_codebuild as _codebuild,
)
from constructs import Construct
import os
import yaml


class Ecrstack(Stack):
    def __init__(self, scope: Construct, id: str,model_info,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        project_id = model_info["project_id"]
        ecr_repo_name = model_info['ecr_repository_name']
     
        # Create ECR Repo
        _ecr.Repository(self, ecr_repo_name, repository_name=ecr_repo_name)
        account_id = model_info["account_id"]
        region =  model_info["region"]
        current_timestamp = model_info["tag"]
        # Generate ECR Full repo name
        full_ecr_repo_name = f'{account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_repo_name}:{current_timestamp}'
        
        build_spec_yml = ''

        with open("buildspec.yml", "r") as stream:
            try:
                build_spec_yml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        # Trigger CodeBuild job
        containerize_build_job =_codebuild.Project(
            self,
            f"lambda_rag_llm_container_{project_id}",
            build_spec=_codebuild.BuildSpec.from_object_to_yaml(build_spec_yml),
            environment = _codebuild.BuildEnvironment(
            build_image=_codebuild.LinuxBuildImage.STANDARD_6_0,
            privileged=True,
            environment_variables={
                "ecr_repo": _codebuild.BuildEnvironmentVariable(value = full_ecr_repo_name),
                "account_id" : _codebuild.BuildEnvironmentVariable(value = model_info["account_id"]),
                "region": _codebuild.BuildEnvironmentVariable(value = model_info["region"])
            })
        )
        
        ecr_policy = _iam.PolicyStatement(actions=[
        "ecr:BatchCheckLayerAvailability", "ecr:CompleteLayerUpload", "ecr:GetAuthorizationToken",
        "ecr:InitiateLayerUpload", "ecr:PutImage", "ecr:UploadLayerPart", "ecr:CreateRepository",
        "lambda:PublishLayerVersion"
        ], resources=["*"])
        containerize_build_job.add_to_role_policy(ecr_policy)
        self.project_name_repo =  containerize_build_job.project_name
        
        

        
        
