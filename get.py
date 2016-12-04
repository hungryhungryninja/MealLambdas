import boto3
import json

def parse_typed_struct(typed_struct):
    """
    Recursively parse and 'flatten' a typed structure of the sort returned by
    DynamoDB's scan methods.
    """
    if len(typed_struct.keys()) == 1:
        for key in typed_struct:
            if key == 'S':
                return str(typed_struct[key])
            if key == 'N':
                return int(typed_struct[key])
            if key == 'M':
                for sub_key in typed_struct[key]:
                    if isinstance(typed_struct[key][sub_key], dict):
                        typed_struct[key][sub_key] = parse_typed_struct(typed_struct[key][sub_key])
                return dict(typed_struct[key])
            if key == 'L':
                for idx, elem in enumerate(typed_struct[key]):
                    if isinstance(elem, dict):
                        typed_struct[key][idx] = parse_typed_struct(typed_struct[key][idx])
                return list(typed_struct[key])
    else:
        for key in typed_struct:
            if isinstance(typed_struct[key], dict):
                typed_struct[key] = parse_typed_struct(typed_struct[key])

def lambda_handler(input, context):
    client = boto3.client('lambda')

    params = {}

    # Check whether query parameters were passed in or whether
    # it has a message in the body
    if 'id' in input['body-json']:
        params['id'] = input['body-json']['id']
    elif 'id' in input['params']['path']:
        params['id'] = int(input['params']['path']['id'])

    # Create the search object we'll pass to the lambda endpoint
    search = {}
    if "id" in params:
        search = {
            "table_name": "Meals",
            "type": "get_id",
            "id_keys": params
        }
    else:
        search = {
            "table_name": "Meals",
            "type": "query",
            "match_attributes": params
        }

    response = client.invoke(
        FunctionName='DALSearch',
        InvocationType='RequestResponse',
        Payload=json.dumps(search)
    )

    read_response = json.loads(response['Payload'].read())

    if isinstance(read_response, list):
        for rec in read_response:
            parse_typed_struct(rec)
    
    return read_response
