import os

import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()


assert os.getenv("DO_SPACE_ACC_KEY_ID", "DO801HA26UWHUP2YX7R3"), "Missing access key"
assert os.getenv("DO_SPACE_READ_KEY", "r3tRgt/5R+xURxVsbTMZXjSg4Yvv1Zsp3v1mfphUQjg"), (
    "Missing secret key"
)
assert os.getenv(
    "DO_SPACE_ENDPOINT", "https://pdatastore.sgp1.digitaloceanspaces.com"
), "Missing endpoint"

session = boto3.session.Session()

client = session.client(
    "s3",
    region_name="sgp1",
    endpoint_url="https://pdatastore.sgp1.digitaloceanspaces.com",
    aws_access_key_id="DO801HA26UWHUP2YX7R3",
    aws_secret_access_key="r3tRgt/5R+xURxVsbTMZXjSg4Yvv1Zsp3v1mfphUQjg",
    config=Config(signature_version="s3v4"),
)

# for c in dir(client):
#     print(c)
client.upload_file(
    "files/O'Reilly - SSH The Secure Shell The Definitive Guide-2.pdf",
    "SSH.pdf",
)
