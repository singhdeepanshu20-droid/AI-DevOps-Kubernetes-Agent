import sys
import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

# Ensure backend root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

def create_dynamodb_table():
    print(f"Connecting to AWS DynamoDB in region '{settings.AWS_REGION}'...")
    
    boto_config = Config(connect_timeout=4, read_timeout=4, retries={"max_attempts": 1})
    session_kwargs = {"region_name": settings.AWS_REGION, "config": boto_config}
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

    try:
        dynamodb = boto3.resource("dynamodb", **session_kwargs)
        table_name = settings.AWS_DYNAMODB_TABLE

        table = dynamodb.Table(table_name)
        table.load()
        print(f"✅ AWS DynamoDB table '{table_name}' already exists and is active!")
        return
    except ClientError as err:
        if err.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"⏳ Creating AWS DynamoDB table '{table_name}'...")
            try:
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {"AttributeName": "id", "KeyType": "HASH"}  # Partition Key
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "id", "AttributeType": "S"}
                    ],
                    BillingMode="PAY_PER_REQUEST"
                )
                print(f"Waiting for table '{table_name}' to finish creation on AWS...")
                table.wait_until_exists()
                print(f"🎉 Successfully created AWS DynamoDB table '{table_name}'!")
            except Exception as e:
                print(f"❌ Failed to create DynamoDB table: {e}")
        else:
            print(f"❌ Error checking DynamoDB table: {err}")
    except (BotoCoreError, Exception) as e:
        print(f"⚠️ AWS Connection error ({e}). Ensure your AWS credentials in .env are valid and have DynamoDB permissions.")

if __name__ == "__main__":
    create_dynamodb_table()
