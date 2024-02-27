import os

import boto3
from botocore.credentials import Credentials
from requests_aws4auth import AWS4Auth

from gen_ai.config import envs


def should_verify_certs(opensearch_url):
    is_local = (
            os.getenv("DEPLOY_ENV") == "local"
            or opensearch_url.startswith("http://localhost")
            or opensearch_url.startswith("http://host")
    )
    return not is_local


def get_credentials():
    credentials = (
        boto3.Session().get_credentials()
        if os.getenv("DEPLOY_ENV") != "local"
        else Credentials(
            access_key="accesskey",
            secret_key="serectkey",
            token="token",
        )
    )
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        envs.get("aws_region"),
        "es",
        session_token=credentials.token,
    )
    return awsauth
