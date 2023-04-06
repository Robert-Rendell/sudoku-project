import json
import boto3
import os
from sudoku import SudokuGenerator, CouldBeIn
import http.client, urllib.parse

def lambda_handler(event, context):
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    
    requestJsonBody = getJsonBodyFromS3Object(bucket, key)
    print(requestJsonBody)

    difficulty = requestJsonBody['difficulty']
    generatorIPAddress = requestJsonBody['generatorIPAddress']
    generatorUserName = requestJsonBody['generatorUserName']
    generationJobId = requestJsonBody['generationJobId']
    
    sg = CouldBeIn();

    puzzle, solution, clues = sg.generate(difficulty)
    body = {
        'puzzle': str(puzzle),
        'solution': str(solution),
        'difficulty': difficulty,
        'clues': clues,
        'generatorIPAddress': generatorIPAddress,
        'generatorUserName': generatorUserName,
        'generationJobId': generationJobId,
        'sudokuInsertionSecurityKey': os.environ.get('SUDOKU_GEN_SECURITY_KEY'),
    }
    
    print("Preparing response message body:")
    print(body)
    
    params = json.dumps(body).encode('utf8')
    # using data parameter makes it POST
    req = urllib.request.Request(
        "https://robrendellwebsite.herokuapp.com/sudoku/add/callback",
        data=params,
        headers={'content-type': 'application/json'}
    )
    response = urllib.request.urlopen(req)
    print(response.status, response.reason)
    
    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }
    
def getJsonBodyFromS3Object(bucket, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('ACCESS_KEY'),
        aws_secret_access_key=os.environ.get('SECRET_KEY'),
    )
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj['Body'].read().decode('utf-8'))
