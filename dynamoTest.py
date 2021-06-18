# --- DynamoDB ---
import boto3

client = boto3.client('dynamodb', aws_access_key_id='fakeMyKeyId', aws_secret_access_key='fakeSecretAccessKey', region_name='eu-central-1', endpoint_url='http://localhost:8000')
music = client.batch_get_item(
    RequestItems={
        'Music': {
            'Keys': [
                {
                    'Artist': {
                        'S': 'No One You Know',
                    },
                    'SongTitle': {
                        'S': 'Call Me Today',
                    },
                }
            ],
            'ProjectionExpression': 'AlbumTitle',
        },
    },
)

user = client.batch_get_item(
    RequestItems={
        'TrainUser': {
            'Keys': [
                {
                    'id': {
                        'N': '3103',
                    },
                    'username': {
                        'S': 'roland@datascientest.com',
                    },
                }
            ],
            'ProjectionExpression': 'username',
        },
    },
)

tables = client.list_tables()
print('--------- -- - -CLIENT DB')
print('user')

print(user)
print('music')
print(music)
print(tables)