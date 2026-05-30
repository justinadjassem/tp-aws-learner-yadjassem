import json
def lambda_handler(event, context):
    print("Event: ", json.dumps(event))

    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object'].get('size', 0)
        print(f"File uploaded: s3://{bucket}/{key} ({size} bytes)")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'S3 event processed successfully',
            'records_count': len(event.get('Records', []))
        })
    }