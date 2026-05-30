import json
import os
import boto3
from datetime import datetime


dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
USER_ID = os.environ.get('USER_ID')


def lambda_handler(event, context):
    print("Event: ", json.dumps(event))
    table = dynamodb.Table(TABLE_NAME)

    results = []

    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object'].get('size', 0)
        file_name = key.split('/')[-1]

        # Check if file already exists in DynamoDB
        response = table.get_item(Key={'userId': USER_ID})
        file_list = response.get('Item', {}).get('fileList', [])

        existing_files = [f['fileName'] for f in file_list]

        if file_name in existing_files:
            print(f"File already exists: {file_name}")
            results.append({'fileName': file_name, 'status': 'already_exists'})
            continue

        # Add file to the list
        new_file = {
            'fileName': file_name,
            'fileSize': size,
            'uploadDate': datetime.utcnow().isoformat(),
            's3Key': key
        }

        table.update_item(
            Key={'userId': USER_ID},
            UpdateExpression='SET fileList = list_append(if_not_exists(fileList, :empty), :newFile)',
            ExpressionAttributeValues={
                ':newFile': [new_file],
                ':empty': []
            }
        )

        print(f"File added: s3://{bucket}/{key} ({size} bytes)")
        results.append({'fileName': file_name, 'status': 'added'})

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'S3 event processed',
            'results': results
        })
    }
