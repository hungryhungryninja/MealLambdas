import boto3
import json

def remove_keys_with_empty_strings(input_dict):
    """
    Removes empty strings from a dictionary. This is done because
    dynamoDB doesn't accept attributes that have empty strings
    for values.
    """
    new_dict = {}
    for k in input_dict:
        if isinstance(input_dict[k], dict):
            new_dict[k] = remove_keys_with_empty_strings(input_dict[k])
        elif isinstance(input_dict[k], list):
            for idx, elem in enumerate(input_dict[k]):
                if isinstance(elem, dict):
                    input_dict[k][idx] = remove_keys_with_empty_strings(elem)
            new_dict[k] = input_dict[k]
        elif input_dict[k] != "":
            new_dict[k] = input_dict[k]
    return new_dict

def get_new_id():
    """
    Retrieves a new key value for the table
    """
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName='DALNewID',
        InvocationType='RequestResponse',
        Payload=json.dumps({'name': 'Meals'})
    )

    response = json.loads(response['Payload'].read())
    return int(response.get('value'))

def lambda_handler(input, context):
    """
    API Endpoint for creating Meals.
    """
    client = boto3.client('lambda')

    input_json = input['body-json']
    input_json = remove_keys_with_empty_strings(input_json)

    # Get a meal id
    input_json['id'] = get_new_id()

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

    if 'FunctionError' in response:
        raise Exception('[BadRequest] ' + response['Payload'].read())

    return '/meals/' + str(input_json['id'])
