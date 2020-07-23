from google.cloud import storage
from flask import send_file
import tempfile

def gcloud_upload(bucket_name,file,destination):
    storage_client = storage.Client.from_service_account_json('restricted/service_upload.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination)

    upload = blob.upload_from_file(file)

    return upload

def gcloud_retrieve(bucket_name, blob_name, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    with tempfile.NamedTemporaryFile() as temp:
        blob.download_to_filename(temp.name)
        return send_file(temp.name, attachment_filename=filename)

