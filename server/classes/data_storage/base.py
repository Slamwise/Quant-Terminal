from classes.base import DataStorage
import os
import boto3
from botocore.exceptions import NoCredentialsError, EndpointConnectionError
import aiofiles

class LocalStorage(DataStorage):
    async def connect(self):
        # For local storage, the connection might not be necessary
        return os.path.exists(self.path)

    async def check_connectivity(self):
        # Check if the path is accessible asynchronously
        return os.access(self.path, os.W_OK)

    async def get_storage_remaining(self):
        # Async versions of disk usage might require threading or process pools
        pass
    
    async def list_files(self):
        return os.listdir(self.path)
    
    async def save_file(self, file_name, data):
        full_path = os.path.join(self.path, file_name)
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(data)
            f.write(data)
    
    
class CloudStorage(DataStorage):
    def __init__(self, name, bucket_name, aws_access_key, aws_secret_key):
        super().__init__(name, 'cloud')
        self.bucket_name = bucket_name
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.s3_client = None
    
    async def connect(self):
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
            # Check if bucket exists
            await self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except (NoCredentialsError, EndpointConnectionError):
            return False
    
    async def check_connectivity(self):
        try:
            await self.s3_client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
            return True
        except Exception:
            return False
    
    async def get_storage_remaining(self):
        # S3 doesn't have a storage limit, but you can calculate usage
        total_size = 0
        paginator = self.s3_client.get_paginator('list_objects_v2')
        async for page in paginator.paginate(Bucket=self.bucket_name):
            for obj in page.get('Contents', []):
                total_size += obj['Size']
        return {'total_used': total_size}
    
    async def list_files(self):
        objects = await self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        return [obj['Key'] for obj in objects.get('Contents', [])]
    
    async def save_file(self, file_name, data):
        await self.s3_client.put_object(Bucket=self.bucket_name, Key=file_name, Body=data)