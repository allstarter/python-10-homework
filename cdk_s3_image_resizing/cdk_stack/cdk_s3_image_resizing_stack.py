from constructs import Construct
from aws_cdk import (
    CfnParameter,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_iam,
    aws_sqs,
    aws_sns,
    aws_sns_subscriptions, 
    aws_s3,
    aws_s3_notifications,
    aws_logs,
    aws_lambda,
    aws_lambda_event_sources as aws_lambda_events,
    aws_lambda_python_alpha as aws_lambda_python
)


class CdkS3ImageResizingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Fetch current IDs of AWS account and region
        AWS_ACCOUNT_ID = Stack.of(self).account
        AWS_REGION = Stack.of(self).region
        BUCKET_NAME = f"upload-bucket-{AWS_ACCOUNT_ID}-{AWS_REGION}"

        # Value Lambda timeout and SQS parameters
        TIMEOUT_SECONDS = 120
        VISIBILTY_TIMEOUT_QUEUE = Duration.seconds(TIMEOUT_SECONDS * 6)
        MAX_EVENT_AGE_LAMBDA = Duration.minutes(TIMEOUT_SECONDS / 10)
        TIMEOUT_LAMBDA = Duration.seconds(TIMEOUT_SECONDS)

        dead_letter_queue = aws_sqs.Queue(
            self,
            id='s3_s3_upload_dlq',
            retention_period=Duration.days(7)
        )

        upload_queue = aws_sqs.Queue(
            self,
            id='s3_upload_queue',
            dead_letter_queue=aws_sqs.DeadLetterQueue(
                max_receive_count=1,
                queue=dead_letter_queue
            ),
            visibility_timeout=VISIBILTY_TIMEOUT_QUEUE
        )

        bucket = aws_s3.Bucket(
            self,
            'S3UploadBucket',
            bucket_name=BUCKET_NAME,
            versioned=False,
            encryption=aws_s3.BucketEncryption.S3_MANAGED,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # You shouldn't use `lambda` as a name in Python
        lambda_function = aws_lambda_python.PythonFunction(
            scope=self,
            id='S3ImageResizingLambda',
            entry='./lambda',  # Path to function code
            description='S3 image resizing',
            handler='handler',
            index='handler.py',
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
            max_event_age=MAX_EVENT_AGE_LAMBDA,
            retry_attempts=1,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            memory_size=512,
            timeout=TIMEOUT_LAMBDA,
            tracing=aws_lambda.Tracing.DISABLED
        )

        # Lambda policy to enable S3 object access
        lambda_function.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                resources=[f"{bucket.bucket_arn}/*"],
                actions=['s3:GetObject', 's3:PutObject', 's3:DeleteObject']
            )
        )

        upload_sqs_subscription = aws_sns_subscriptions.SqsSubscription(
            upload_queue,
            raw_message_delivery=True
        )

        upload_event_topic = aws_sns.Topic(
            self,
            id='upload_topic'
        )

        # This binds the SNS Topic to the SQS Queue
        upload_event_topic.add_subscription(upload_sqs_subscription)

        # If you don't specify a filter all uploads will trigger an event.
        # Also, modifying the event type will handle other object operations
        bucket.add_event_notification(
            aws_s3.EventType.OBJECT_CREATED_PUT,
            aws_s3_notifications.SnsDestination(upload_event_topic),
            aws_s3.NotificationKeyFilter(prefix='uploads', suffix='.jpg')
        )

        # This binds the lambda to the SQS Queue
        invoke_event_source = aws_lambda_events.SqsEventSource(upload_queue)
        lambda_function.add_event_source(invoke_event_source)

        # CloudFormation outputs
        CfnOutput(
            self,
            'UploadFileToS3Example',
            value=f"aws s3 cp <local-path-to-file> s3://{BUCKET_NAME}/",
            description='Upload a file to S3 '
            '(using AWS CLI) to trigger the SQS chain',
        )
        CfnOutput(
            self,
            'UploadSqsQueueUrl',
            value=upload_queue.queue_url,
            description='Link to the SQS Queue triggered on S3 uploads',
        )
        CfnOutput(
            self,
            'LambdaFunctionName',
            value=lambda_function.function_name,
        )
        CfnOutput(
            self,
            'LambdaFunctionLogGroupName',
            value=lambda_function.log_group.log_group_name,
        )
