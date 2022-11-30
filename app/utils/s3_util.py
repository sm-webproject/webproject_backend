"""s3 관련 모듈"""
import typing
import nanoid

import boto3

from env import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_S3_BUCKET_NAME

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def upload_file(file: typing.IO, file_extension: str, folder: str = ""):
    """
    upload file
    """
    file_name = nanoid.generate() + ("." + file_extension) if file_extension else None
    if len(folder) > 0:
        folder += '/'
    s3.upload_fileobj(file, AWS_S3_BUCKET_NAME, folder + file_name,
                      ExtraArgs={'ACL': 'public-read'})
    return file_name
