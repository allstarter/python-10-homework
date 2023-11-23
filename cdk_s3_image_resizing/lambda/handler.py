import json
import boto3
# from io import BytesIO
# from PIL import Image

client = boto3.client('s3')

def lambda_handler(event, context):
    print(event)
    try:
        
        for item in event['Records']:
            
            s3_event = json.loads(item['body'])
            
            if 'Event' in s3_event and s3_event['Event'] == 's3:TestEvent':
                print("Test Event")
                
            else:
                for item in s3_event['Records']:
                    bucket = item['s3']['bucket']['name']
                    key = item['s3']['object']['key']
                    print(f"Lambda triggerd by upload of {bucket}/{key}")
                        
    except Exception as exception:
        print(exception)
