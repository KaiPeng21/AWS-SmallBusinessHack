# AWS Small Business Hackathon

- [Introduction](##Introduction)
- [Demo](#Preview%20Demo)
- [Design Architecture](##Design%20Architecture)
- [Fronend Repository](##Frontend%20Repository)
- [Install Prerequisites](##Install%20Prerequisites)
- [Setup Development Environment](##Setup%20Development%20Environment)
- [Testing Application Locally](##Testing%20Application%20Locally)
- [Deploy your App onto AWS](##Deploy%20your%20App%20onto%20AWS)
- [App Testing Instructions](##App%20Testing%20Instructions)
- [Liscense](##Liscense)

## Introduction

Use [Serverless Technology](https://aws.amazon.com/lambda/), [Elasticsearch](https://www.elastic.co/), and [Amazon Machine Learning and AI Services](https://aws.amazon.com/machine-learning/) to determine if a company will make it to Crunchbase top 50k list based on it’s projects funded by SBIR.

This is the backend API Core. The frontend code is in [another](https://github.com/87maza/aws-sba) repository.

## Preview Demo

![](images/sba-frontend.png)
Frontend with a search engine and a filter table.

![](images/sba-frontend2.png)
Visualizing the award and probability of success in a scatter plot.

![](images/bot.gif)
A chatbot which may interface with messaging platform like Slack or Facebook Messenger.

![](images/sba-es.png)
You can also you Kibina to search the trained database.

## Design Architecture

![](images/sba-architect.png)

## Frontend Repository

[AWS-SBA Frontend Development in React JS](https://github.com/87maza/aws-sba)

#### AWS Services and Resources Utilized

###### Compute
* **Lambda**: serverless compute
    * **Search Api**: Interfaces with Elasticsearch and Api Gateway.
    * **Lex Hook**: Interfaces with Amazon Lex. Retrieves information from Elasticsearch and have the bot sending a response over the lex response card.

###### Storage and Analytics
* **S3**: Stores the document file objects.
* **Elasticsearch**: Search enginge database.

###### Machine Learning
* **Comprehend**: Detects the key phrases in the context. 
* **Comprehend Customized**: Trained customized data using comprehend.
* **Lex**: Natrual language processing service that interfaces the app backend with a messaging platform.
* **SageMaker**: Trained probability of success and insert result into Elasticsearch

###### Management and Governance
* **CloudFormation**: maintain and deploy the AWS infrastructure as code
* **AWS SAM**: build the next stage CloudFormation template

## Install Prerequisites

- [Python 3.6](https://www.python.org/downloads/)
- [Pipenv](https://github.com/pypa/pipenv)
    ```
    $ pip3 install pipenv --upgrade
    ```
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) 
    ```
    $ pip install awscli --upgrade --user
    ```

## Setup Development Environment

#### Configure the AWS CLI credentials

[AWS Configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) command is the fastest way to set up your AWS CLI installation.

```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

#### Setup Virtual Environment with Pipenv

[Pipenv](https://github.com/pypa/pipenv) is a dependency management tool for python, which creates and manages a virtualenv for your dependencies.

Install the development package in your virtual environment:
```
$ export PIPENV_VENV_IN_PROJECT=true && pipenv install --three --dev
```

Enter your virtual environment:
```
$ pipenv shell
```

To exit the virtual environment:
```
$ exit
```

## Testing Application Locally

#### Configure a  local Elasticsearch instance for testing
You can install [Elasticsearch 6.3](https://www.elastic.co/guide/en/elasticsearch/reference/6.3/install-elasticsearch.html) locally or use [Docker](https://hub.docker.com/r/nshou/elasticsearch-kibana/) to simulate a Elasticsearch enviornment.

Create an Elasticsearch and Kibana instance from Docker
```
$ docker run --name esml-es-test -d -p 9200:9200 -p 5601:5601 nshou/elasticsearch-kibana
```

Debug and test your Elasticsearch using [Kibana](https://www.elastic.co/products/kibana) from http://localhost:5601

## Deploy your App onto AWS

#### Build your application from the makefile
A [makefile](makefile) is provided to help migrating your python source code and dependencies in pipenv to AWS Lambda.
```
$ make
```

#### Deploy the infrastructure from AWS SAM and CloudFormation template
This project uses AWS Serverless Application Models and CloudFormation templates to configure and maintain the AWS infrastructure.

Deploy using "dev" deployment stage:
```
$ ./deploy.sh
```

or giving a different deployment stage name by:

```
$ ./deploy.sh <deployment-stage>
```

A [deploy.sh](deploy.sh) shell script is provided to help building the next stage CloudFormation template from [template.yaml](template.yaml) and creating your CloudFormation stack on AWS.

#### Importing Amazon Lex 

CloudFormation does not yet have an Amazon Lex resource and property types. An Amazon Lex template json is provided in the [lex/](/lex) directory. 

##### Add Lex Hook Lambda Arn to the template file:

After your CloudFormation stack status turns to CREATE_COMPLETE or UPDATE_COMPLETE, go to your AWS lambda console and find the lex_hook function ARN. Add the lambda ARN to the specified section in the Amazon Lex template.

##### Import template file to Amazon Lex

Follow the instructions [here](https://docs.aws.amazon.com/lex/latest/dg/import-export-lex.html) to import Lex template to the cloud from the console or from the CLI.

#### Integrating your bot with Slack or other messaging platform

Follow the instructions [here](https://docs.aws.amazon.com/lex/latest/dg/slack-bot-association.html) to integrate your bot with external messaging platform.

## App Testing Instructions

1. Deploy the application by following the above steps.
2. Put image (jpg or png) or pdf documents to the document store S3 bucket.
3. Ask the bot to "search for a doc" as shown in the Preview Demo section.

## Liscense

[MIT License](LICENSE)

