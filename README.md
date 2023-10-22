

# Overview!

This project is a CDK template for deploying an architecture on AWS consisting of a gateway api, and a lambda function connected to a sagemaker endpoint. It has been used to deploy Falcon, Llama and Stablediffusion models.

# Prerequisite

The AWS CDK uses Node.js (>= 10.13.0, except for versions 13.0.0 - 13.6.0). A version in active long-term support (16.x at this writing) is recommended.

To install Node.js visit the node.js [website](https://nodejs.org/).
If you already have Node.js installed, verify that you have a compatible version:

```
$ node --version
```
Output should be >= 10.13.0

Next, we’ll install the AWS CDK Toolkit. The toolkit is a command-line utility which allows you to work with CDK apps.

Open a terminal session and run the following command:

 * Windows: you’ll need to run this as an **Administrator**
 * POSIX: on some systems you may need to run this with sudo 

```
$ npm install -g aws-cdk
```
You can check the toolkit version:

```
$ cdk --version
```


# Get started!

Clone the project and, in the cdk_mirage_project folder, create a virtual environment for the next step.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

## Steps

 * Install the AWS CLI and configure it. 
 * Then create a sagemaker with the necessary accesses, perhaps fullaccess. Get the arn
 * Create your model and retrieve the endpoint name.
 * Open the app.py file and replace the arn and endpoint values.
 * don't forget to give your stack a new name

```
mirageStack(app, "name of your stack",model_info=MODEL_INFO)
```

The first time you deploy an AWS CDK app into an environment (account/region), you’ll need to install a "bootstrap stack". This stack includes resources that are needed for the toolkit’s operation. 

You can use the cdk bootstrap command to install the bootstrap stack into an environment:

```
$ cdk bootstrap
```

After that, use cdk deploy to deploy a CDK app:


```
$ cdk deploy
```

## Note:

I've added a folder called **draft** which contains the lambda functions used for each model. The lambda used for deployment is **\lambda\lambda_handler.py** . It's in this file that you'll need to make any necessary modifications.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
