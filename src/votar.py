import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
votes_table = dynamodb.Table(os.environ['VOTES_TABLE'])
connections_table = dynamodb.Table(os.environ['CONNECTIONS_TABLE'])

def lambda_handler(event, context):
    # 1. Extraer datos del mensaje
    body = json.loads(event.get('body', '{}'))
    opcion = body.get('opcionId') # Ejemplo: "Candidato_A"
    
    if not opcion:
        return {'statusCode': 400, 'body': 'Falta opcionId'}

    # 2. Incrementar el voto de forma atómica
    votes_table.update_item(
        Key={'opcionId': opcion},
        UpdateExpression="ADD votos :inc",
        ExpressionAttributeValues={':inc': 1}
    )

    # 3. Obtener el estado actual de la votación
    todos_los_votos = votes_table.scan()['Items']
    data_to_send = json.dumps(todos_los_votos)

    # 4. Enviar a todos los clientes conectados
    # Configuramos el cliente para hablar con API Gateway
    domain = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url=f"https://{domain}/{stage}")

    # Escaneamos todos los IDs de conexión
    connections = connections_table.scan(ProjectionExpression="connectionId")['Items']

    for conn in connections:
        cid = conn['connectionId']
        try:
            gatewayapi.post_to_connection(ConnectionId=cid, Data=data_to_send)
        except gatewayapi.exceptions.GoneException:
            # Si la conexión ya no existe, la borramos
            connections_table.delete_item(Key={'connectionId': cid})
        except Exception as e:
            print(f"Error enviando a {cid}: {e}")

    return {'statusCode': 200}
