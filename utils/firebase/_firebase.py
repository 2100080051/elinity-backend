import json
import os
import firebase_admin
from firebase_admin import credentials, messaging


def load_firebase_credentials():
    file_path = os.path.join(os.path.dirname(__file__), 'credentials', 'firebase.json')
    with open(file_path, 'r') as file:
        credentials = json.load(file)
    return credentials

# setting up firebase credentials
firebase_credentials = load_firebase_credentials()
firebase_cred = credentials.Certificate(firebase_credentials)
firebase_app = firebase_admin.initialize_app(firebase_cred)


class Firebase:
    
    @staticmethod
    def send_topic_push(topic,title, body):
        message = messaging.Message(
        notification=messaging.Notification(
        title=title,
        body=body
        ),
        topic=topic
        )
        messaging.send(message) 

    @staticmethod
    def send_token_push(title, body, tokens,metadata):
        # Stringify values in the dictionary
        metadata_str = {k: str(v) for k, v in metadata.items()}
 
        message = messaging.MulticastMessage(
        notification = messaging.Notification(title=title,body=body),
        tokens=tokens,
        data=metadata_str
        )
        messaging.send_multicast(message)