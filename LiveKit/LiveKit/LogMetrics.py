
import os
import json
from livekit.agents.metrics import LLMMetrics, STTMetrics, TTSMetrics, EOUMetrics
from azure.storage.blob.aio import BlobServiceClient
from dotenv import load_dotenv
import asyncio
import aiofiles

load_dotenv()

AZURE_LOGS_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_LOGS_STORAGE_ACCOUNT_NAME")
AZURE_LOGS_CONNECTION_STRING = os.getenv("AZURE_LOGS_CONNECTION_STRING")
AZURE_LOGS_CONTAINER_NAME=os.getenv("AZURE_LOGS_CONTAINER_NAME")

async def upload_file_to_blob(file_path, blob_name, max_retries=3):
    # try:
    #     async with BlobServiceClient.from_connection_string(AZURE_LOGS_CONNECTION_STRING) as blob_service_client:
    #         blob_client = blob_service_client.get_blob_client(container=AZURE_LOGS_CONTAINER_NAME, blob=blob_name)

    #         with open(file_path, "rb") as data:
    #             await blob_client.upload_blob(data, overwrite=True)

    #         print(f"Uploaded {blob_name} from file {file_path}")
    # except Exception as e:
    #     print(f"Error uploading file: {e}")
    for attempt in range(max_retries):
        try:
            async with BlobServiceClient.from_connection_string(AZURE_LOGS_CONNECTION_STRING) as blob_service_client:
                blob_client = blob_service_client.get_blob_client(container=AZURE_LOGS_CONTAINER_NAME, blob=blob_name)

                async with aiofiles.open(file_path, "rb") as data:
                    file_content = await data.read()

                await blob_client.upload_blob(file_content, timeout=30)
                print(f"Uploaded {blob_name} from file {file_path}.")
                return  

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt + 1 == max_retries:
                print(f"Failed to upload {blob_name} after {max_retries} attempts")
            else:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s

def serialize_metrics(obj):
    if isinstance(obj, (LLMMetrics, STTMetrics, TTSMetrics, EOUMetrics)):
        return obj.__dict__

# def save_to_file(file_content, filename):

#     path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_metrics')

#     if not os.path.exists(path):
#         os.makedirs(path)

#     #content = json.dumps(file_content, indent=4, default=serialize_metrics)

#     try:
#         with open(os.path.join(path,f"{filename}.txt"),"w") as file:
#             file.write(file_content)
#             print(f"Saved {filename} to local file system")

#     except Exception as e:
#         print(e)


async def save_to_file(file_content, filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_metrics')
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, f"{filename}.txt")
    try:
        async with aiofiles.open(file_path, "w") as file:
            await file.write(file_content)
        print(f"Saved {filename} to local file system")
        return file_path  
    except Exception as e:
        print(f"Error saving file: {e}")
        raise