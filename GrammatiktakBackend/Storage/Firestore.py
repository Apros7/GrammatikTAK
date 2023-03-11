from google.cloud import datastore

# used to save text, spellingerrors and feedback to Google Cloud Firestore

class FirestoreClient():
    def __init__(self):
        # Initializes client with secret key: DO NOT SHARE OR COMMIT
        key_path = "Keys/serviceAccountKey.json"
        self.client = datastore.Client.from_service_account_json(key_path)

    # save input (text) when correcting the text
    # if the input is larger than 1500 bytes, it is split up into 1500 byte objects and saved due to Firestore Limits
    def save_input(self, input):
        kind = 'Backend-alltext'
        input_bytes = input.encode('utf-8')
        max_bytes_per_entity = 1500
        num_entities = (len(input_bytes) + max_bytes_per_entity - 1) // max_bytes_per_entity
        input_entity = datastore.Entity(self.client.key(kind))
        input_entity_dict = {}

        for i in range(num_entities):
            start = i * max_bytes_per_entity
            end = start + max_bytes_per_entity
            input_chunk = input_bytes[start:end].decode('utf-8')
            input_entity_dict[f"text{i}"] = input_chunk

        input_entity.update(input_entity_dict)
        self.client.put(input_entity)
        print("Text sent to firestore")

    # save input (text) and feedback when feedback button is pressed
    # if the input/feedback is larger than 1500 bytes, it is split up into 1500 byte objects and saved due to Firestore Limits
    def save_feedback(self, feedback, text):
        kind = 'Feedback'
        feedback_bytes = feedback.encode('utf-8')
        text_bytes = text.encode('utf-8')
        max_bytes_per_entity = 1500
        num_entities_feedback = (len(feedback) + max_bytes_per_entity - 1) // max_bytes_per_entity
        num_entities_text = (len(text) + max_bytes_per_entity - 1) // max_bytes_per_entity

        feedback_entity = datastore.Entity(self.client.key(kind))
        feedback_entity_dict = {}

        for i in range(num_entities_feedback):
            start = i * max_bytes_per_entity
            end = start + max_bytes_per_entity
            feedback_chunk = feedback_bytes[start:end].decode('utf-8')
            feedback_entity_dict[f"feedback{i}"] = feedback_chunk
        
        for i in range(num_entities_text):
            start = i * max_bytes_per_entity
            end = start + max_bytes_per_entity
            text_chunk = text_bytes[start:end].decode('utf-8')
            feedback_entity_dict[f"text{i}"] = text_chunk

        feedback_entity.update(feedback_entity_dict)
        self.client.put(feedback_entity)
        print("Feedback sent to firestore")