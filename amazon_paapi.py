import boto3
from botocore.exceptions import ClientError
import os

client = boto3.client(
    "aps",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1"
)

def get_amazon_price(asins: list[str]):
    try:
        response = client.get_items(
            ItemIds=asins,
            Resources=["Offers.Listings.Price"]
        )
        items = response.get("ItemsResult", {}).get("Items", [])
        return {
            item["ASIN"]: item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("Amount")
            for item in items
        }
    except ClientError:
        return {}