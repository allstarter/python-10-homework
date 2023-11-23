Homework #10 of Python starter training
=========

### Alexa demo skill using CDK and boto3
As promised you will find the code for deploying your own Alexa skill for report on AWS Cloud Formation Stack here
https://github.com/allstarter/python-10-homework/cdk_alexa_demo/

It include a short README file to help you to get all prerequisites in place.
Have fun, if you are keen to playing around with it.

### Homework:
In folder s3_image_resizing you find code to start with AWS Lambda to build an automatic image resizing for an S3 bucket. Please complete following:

* Create S3 bucket, SQS queue, IAM roles and dummy Lambda. There are 2 ways
  * You can use CDK app in folder `cdk_s3_image_resizing`
  * Alternatively you can use AWS Cloud Formation together with `cfn_s3_image_resizing.yaml`
* Please implement the image resizing in Lambda code in subproject `cdk_s3_image_resizing\lambda`


> [!NOTE]
> Please use virtual environment as recommended in [session 07](https://github.com/allstarter/python-07-homework).
> * Open cmd as an Administrator
> * cd into project folder
> * Upgrade pip before creating virtual environment to avoid errors with \
> `python.exe -m pip install --upgrade pip`
> * Install venv `python -m venv .venv`
> * Enter venv running `.venv\Scripts\activate.bat`
> * Install packages with `pip install -r requirements.txt`
> 
> You are ready to code now. Try `code .`
