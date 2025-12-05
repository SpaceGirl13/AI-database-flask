# ==================================================
# File: joke_api.py (rename from ai_concepts_api.py)
# ==================================================

from flask import Blueprint, jsonify
from flask_restful import Api, Resource
import requests
import random

from hacks.jokes import *

joke_api = Blueprint('joke_api', __name__,
                   url_prefix='/api/jokes')

api = Api(joke_api)

class JokesAPI:
    # not implemented
    class _Create(Resource):
        def post(self, joke):
            pass
            
    # getJokes()
    class _Read(Resource):
        def get(self):
            return jsonify(getJokes())

    # getJoke(id)
    class _ReadID(Resource):
        def get(self, id):
            return jsonify(getJoke(id))

    # getRandomJoke()
    class _ReadRandom(Resource):
        def get(self):
            return jsonify(getRandomJoke())
    
    # getRandomJoke()
    class _ReadCount(Resource):
        def get(self):
            count = countJokes()
            countMsg = {'count': count}
            return jsonify(countMsg)

    # put method: addJokeHaHa
    class _UpdateLike(Resource):
        def put(self, id):
            addJokeHaHa(id)
            return jsonify(getJoke(id))

    # put method: addJokeBooHoo
    class _UpdateJeer(Resource):
        def put(self, id):
            addJokeBooHoo(id)
            return jsonify(getJoke(id))

    # building RESTapi resources/interfaces, these routes are added to Web Server
    api.add_resource(_Create, '/create/<string:joke>', '/create/<string:joke>/')
    api.add_resource(_Read, "", '/')
    api.add_resource(_ReadID, '/<int:id>', '/<int:id>/')
    api.add_resource(_ReadRandom, '/random', '/random/')
    api.add_resource(_ReadCount, '/count', '/count/')
    api.add_resource(_UpdateLike, '/like/<int:id>', '/like/<int:id>/')
    api.add_resource(_UpdateJeer, '/jeer/<int:id>', '/jeer/<int:id>/')

if __name__ == "__main__": 
    # server = "http://127.0.0.1:5000" # run local
    server = 'https://flask.opencodingsociety.com' # run from web
    url = server + "/api/jokes"
    responses = []

    # get count of jokes on server
    count_response = requests.get(url+"/count")
    count_json = count_response.json()
    count = count_json['count']

    # update likes/dislikes test sequence
    num = str(random.randint(0, count-1)) # test a random record
    responses.append(
        requests.get(url+"/"+num)  # read joke by id
        ) 
    responses.append(
        requests.put(url+"/like/"+num) # add to like count
        ) 
    responses.append(
        requests.put(url+"/jeer/"+num) # add to jeer count
        ) 

    # obtain a random joke
    responses.append(
        requests.get(url+"/random")  # read a random joke
        ) 

    # cycle through responses
    for response in responses:
        print(response)
        try:
            print(response.json())
        except:
            print("unknown error")


# ==================================================
# File: hacks/jokes.py
# Data model for AI concepts (but keeping joke structure)
# ==================================================

# AI concepts data - using "joke" field name for compatibility
jokes_data = [
    {
        "id": 1,
        "joke": "Prompt Engineering: Crafting effective instructions to guide AI responses",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 2,
        "joke": "Large Language Models (LLMs): Neural networks trained on vast text data",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 3,
        "joke": "Tokens: The basic units of text that AI models process",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 4,
        "joke": "Temperature: Controls randomness vs. predictability in AI outputs",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 5,
        "joke": "Fine-tuning: Adapting a pre-trained model for specific tasks",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 6,
        "joke": "RAG (Retrieval-Augmented Generation): Combining AI with external knowledge",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 7,
        "joke": "Context Window: The amount of text an AI can process at once",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 8,
        "joke": "Embeddings: Numerical representations of text for similarity comparison",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 9,
        "joke": "Few-Shot Learning: Teaching AI through examples in the prompt",
        "haha": 0,
        "boohoo": 0
    },
    {
        "id": 10,
        "joke": "Hallucination: When AI generates false or nonsensical information",
        "haha": 0,
        "boohoo": 0
    }
]


def getJokes():
    """Return all jokes"""
    return jokes_data


def getJoke(id):
    """Return a specific joke by ID"""
    for joke in jokes_data:
        if joke['id'] == id:
            return joke
    return {"error": "Joke not found"}, 404


def getRandomJoke():
    """Return a random joke"""
    return random.choice(jokes_data)


def countJokes():
    """Return the count of jokes"""
    return len(jokes_data)


def addJokeHaHa(id):
    """Increment the 'haha' count for a joke"""
    for joke in jokes_data:
        if joke['id'] == id:
            joke['haha'] += 1
            return joke
    return {"error": "Joke not found"}, 404


def addJokeBooHoo(id):
    """Increment the 'boohoo' count for a joke"""
    for joke in jokes_data:
        if joke['id'] == id:
            joke['boohoo'] += 1
            return joke
    return {"error": "Joke not found"}, 404