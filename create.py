import boto3
import json

def lambda_handler(input_json, context):
    """
    API Endpoint for creating Meals.
    """
    client = boto3.client('lambda')

    input_json = input['body-json']

    # Create the create object we'll pass to the lambda endpoint
    create = {
        "table_name": "Meals",
        "item": input_json
    }

    response = client.invoke(
        FunctionName='DALCreate',
        InvocationType='RequestResponse',
        Payload=json.dumps(create)
    )

    return '/meals/' + input_json['id']
