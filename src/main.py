import json
import os
import boto3
from datetime import datetime


dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
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

        # Check if item exists in DynamoDB
        response = table.get_item(Key={'PK': USER_ID})

        if 'Item' not in response:
            # Item doesn't exist, create it with the filename
            item = {'PK': USER_ID, 'filename': [file_name]}
            table.put_item(Item=item)
            print(f"Item created with file: {file_name}")
            results.append({'filename': file_name, 'status': 'created'})
            continue

        file_list = response['Item'].get('filename', [])

        if file_name in file_list:
            print(f"File already exists: {file_name}")
            results.append({'filename': file_name, 'status': 'already_exists'})
            continue

        # Add file to the filename list
        table.update_item(
            Key={'PK': USER_ID},
            UpdateExpression='SET filename = list_append(if_not_exists(filename, :empty), :newFile)',
            ExpressionAttributeValues={
                ':newFile': [file_name],
                ':empty': []
            }
        )

        print(f"File added: s3://{bucket}/{key} ({size} bytes)")
        results.append({'filename': file_name, 'status': 'added'})

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'S3 event processed',
            'results': results
        })
    }
