from google.cloud import datastore

class FirestoreClient():
    def __init__(self):
        key_path = "Keys/serviceAccountKey.json"
        self.client = datastore.Client.from_service_account_json(key_path)
    
    def save_input(self, input):
        kind = 'error'
        input_entity = datastore.Entity(self.client.key(kind))
        input_entity.update({'input': input})
        self.client.put(input_entity)