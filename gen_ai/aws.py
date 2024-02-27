import boto3
from botocore.exceptions import ClientError

from gen_ai.config import envs, is_local_env


def get_s3_client():
    if is_local_env():
        return boto3.client(
            "s3",
            aws_access_key_id="test",
            aws_secret_access_key="test",
            endpoint_url=envs.get("s3_endpoint"),
            region_name=envs.get('aws_region')
        )
    return boto3.client("s3")


def get_s3_path(s3_key):
    bucket_name = envs.get('s3_bucket')
    s3_endpoint = envs.get('s3_endpoint') if is_local_env() else "s3:/"
    return f"{s3_endpoint}/{bucket_name}/{s3_key}"


def create_bucket():
    bucket_name = envs.get('s3_bucket')
    try:
        s3_client = get_s3_client()
        s3_client.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        print(f"Error happened when create bucket {bucket_name}, {e}")
        return False
    return True


def check_bucket_exists():
    bucket_name = envs.get('s3_bucket')
    s3_endpoint = envs.get("s3_endpoint")
    try:
        s3_client = get_s3_client()
        s3_client.head_bucket(Bucket=bucket_name)

        if s3_endpoint.startswith("http://localhost") or s3_endpoint.startswith("http://localstack"):
            cors_configuration = {
                'CORSRules': [{
                    'AllowedHeaders': ['Authorization'],
                    'AllowedMethods': ['GET', 'PUT'],
                    'AllowedOrigins': ['*'],
                    'ExposeHeaders': ['ETag', 'x-amz-request-id'],
                    'MaxAgeSeconds': 3000
                }]
            }
            s3_client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_configuration)
    except ClientError:
        create_bucket()


def upload_file_to_s3(s3_key, file_obj):
    bucket_name = envs.get('s3_bucket')

    # Upload the file
    s3_client = get_s3_client()
    try:
        check_bucket_exists()
        s3_client.upload_fileobj(Fileobj=file_obj, Bucket=bucket_name, Key=s3_key)
    except ClientError as e:
        print(f"Error happened when upload file {s3_key} to bucket {bucket_name}, {e}")


def get_file_from_s3(s3_key):
    bucket_name = envs.get('s3_bucket')

    # Upload the file
    s3_client = get_s3_client()
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status == 200:
            print(f"Successful S3 get_object response from {s3_key}. Status - {status}")
            return response.get("Body").read()
        else:
            print(f"Unsuccessful S3 get_object response from {s3_key}. Status - {status}")
            return False
    except ClientError as e:
        print(f"Error happened when get file {s3_key} from bucket {bucket_name}, {e}")
        return False


def upload_csv_buffer_to_s3(s3_key, buffer):
    bucket_name = envs.get('s3_bucket')

    # Upload the file
    s3_client = get_s3_client()
    try:
        s3_client.put_object(Body=buffer, Bucket=bucket_name, Key=s3_key)
    except ClientError as e:
        print(f"Error happened when upload csv {s3_key} to bucket {bucket_name}, {e}")


def get_file_url(s3_key):
    s3_client = get_s3_client()
    bucket_name = envs.get('s3_bucket')
    try:
        return s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': s3_key})
    except ClientError as e:
        print(f"Error happened when get file {s3_key} url from bucket {bucket_name}, {e}")
        return None
