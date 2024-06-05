import json
import boto3
import requests
import logging

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('arn:aws:dynamodb:us-east-1:905418101464:table/Movies')

API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmYTI1YjBkMGY0ZDU0ZTA4OTRlYjk0YmMwYjZiZTRmNCIsInN1YiI6IjY2MDFlYTE1Yjg0Y2RkMDE2NGY1YjY4MiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Tr2NmEqZ4Ws05q4FbS8NPf-RRqhhEvUvFYHXUtQ0SqU'

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_popular_list():
    url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(url, headers=headers)

    return response.json()

def get_movie_details(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?language=en-US'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def lambda_handler(event, context):
    try:
        items = get_popular_list()
        for item in items['results']:
            movie_id = item['id']
            movie_details = get_movie_details(movie_id)
            to_put = {
            'id': movie_id,
            'name': movie_details['title'],
            'budget': movie_details.get('budget', 0),
            'revenue': movie_details.get('revenue', 0),
            'genres': [genre['name'] for genre in movie_details.get('genres', [])]
            }
            table.put_item(Item=to_put)
    
    except Exception as e:
        logger.error(f"Error occurred: {str(e)} \n {json.dumps(event)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }