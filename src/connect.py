import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['CONNECTIONS_TABLE'])

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    # Guardamos el ID para saber a quién enviarle actualizaciones luego
    table.put_item(Item={'connectionId': connection_id})
    return {'statusCode': 200}
