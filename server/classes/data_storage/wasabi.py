import boto3
import json
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

def save_json_to_wasabi(json_data, bucket_name, object_key, print_success=True):
    """
    Connect to Wasabi and save a JSON block to a specified bucket.
    
    :param json_data: Dict or list to be saved as JSON
    :param bucket_name: Name of the Wasabi bucket
    :param object_key: The key (path) where the JSON will be saved in the bucket
    """
    # Wasabi endpoint URL (replace with your region's endpoint)
    endpoint_url = 'https://s3.wasabisys.com'

    # Get Wasabi credentials from environment variables
    aws_access_key_id = os.getenv('WASABI_ACCESS_KEY')
    aws_secret_access_key = os.getenv('WASABI_SECRET_KEY')

    # Create a boto3 client for Wasabi
    s3_client = boto3.client('s3',
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    try:
        # Convert the JSON data to a string
        json_string = json.dumps(json_data)

        # Upload the JSON string to Wasabi
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json_string,
            ContentType='application/json'
        )
        if print_success:
            print(f"Successfully saved JSON to {bucket_name}/{object_key}")
    except Exception as e:
        print(f"Error saving JSON to Wasabi: {str(e)}")

def test_wasabi_connection_and_list_buckets(print_success=True):
    """
    Test the connection to Wasabi and list available buckets.
    
    :return: List of bucket names if successful, None if connection fails
    """
    # Wasabi endpoint URL (replace with your region's endpoint)
    endpoint_url = 'https://s3.wasabisys.com'

    # Get Wasabi credentials from environment variables
    aws_access_key_id = os.getenv('WASABI_ACCESS_KEY')
    aws_secret_access_key = os.getenv('WASABI_SECRET_KEY')

    # Create a boto3 client for Wasabi
    s3_client = boto3.client('s3',
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    try:
        # Attempt to list buckets
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        if print_success:
            print("Successfully connected to Wasabi.")
            print(f"Available buckets: {', '.join(buckets)}")
        return buckets
    except ClientError as e:
        print(f"Failed to connect to Wasabi: {e}")
        return None

# Example usage:
# json_data = {"key": "value"}
# save_json_to_wasabi(json_data, "your-bucket-name", "path/to/your/file.json")

#List all buckets
# buckets = test_wasabi_connection_and_list_buckets()
# if buckets:
#     print(f"Found {len(buckets)} buckets.")
