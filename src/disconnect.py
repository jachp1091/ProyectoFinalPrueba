import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CONNECTIONS_TABLE'])

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    # Eliminamos el ID cuando el usuario cierra la pestaña
    table.delete_item(Key={'connectionId': connection_id})
    return {'statusCode': 200}
