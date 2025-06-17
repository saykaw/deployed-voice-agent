
import os
import json
from livekit.agents.metrics import LLMMetrics, STTMetrics, TTSMetrics, EOUMetrics
from azure.storage.blob.aio import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

AZURE_LOGS_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_LOGS_STORAGE_ACCOUNT_NAME")
AZURE_LOGS_CONNECTION_STRING = os.getenv("AZURE_LOGS_CONNECTION_STRING")
AZURE_LOGS_CONTAINER_NAME=os.getenv("AZURE_LOGS_CONTAINER_NAME")

async def upload_to_blob_content(file_content, filename):
    try:
        async with BlobServiceClient.from_connection_string(AZURE_LOGS_CONNECTION_STRING) as blob_service_client:
            blob_client = blob_service_client.get_blob_client(container=AZURE_LOGS_CONTAINER_NAME, blob=filename)
            await blob_client.upload_blob(file_content, overwrite=True)
            logger.info(f"Uploaded {filename} to Azure Blob Storage")
    except Exception as e:
        logger.error(f"Failed to upload {filename}: {e}")
        raise

def serialize_metrics(obj):
    if isinstance(obj, (LLMMetrics, STTMetrics, TTSMetrics, EOUMetrics)):
        return obj.__dict__

def save_to_file(file_content, filename):

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_metrics')

    if not os.path.exists(path):
        os.makedirs(path)

    #content = json.dumps(file_content, indent=4, default=serialize_metrics)

    try:
        with open(os.path.join(path,f"{filename}.txt"),"w") as file:
            file.write(file_content)

    except Exception as e:
        print(e)