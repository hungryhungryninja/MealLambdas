import boto3
import json

def lambda_handler(input, context):
    """
    API Endpoint for creating Meals.
    """
    client = boto3.client('lambda')

    key = {"id" : int(input['params']['path']['id'])}

    # Create the create object we'll pass to the lambda endpoint
    create = {
        "table_name": "Meals",
        "key": key
    }

    response = client.invoke(
        FunctionName='DALDelete',
        InvocationType='RequestResponse',
        Payload=json.dumps(create)
    )

    return "deleted"
