"""
ses util
"""
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException

from env import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID

CHARSET = "UTF-8"
SENDER = "no-reply@devfive.kr"


def ses_send_email(receiver: str, title: str, title_inline: str, content: str):
    """
    send email
    """
    client = boto3.client('ses', region_name="ap-northeast-2", aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    with open('utils/ses/email_template.html', 'r', encoding='UTF8') as email_format:
        body_html = email_format.read()
        email_format.close()
        body_html = body_html.replace('email_inline_title', title_inline)
        body_html = body_html.replace('email_inline_content', content)
    try:
        client.send_email(
            Destination={
                'ToAddresses': [
                    receiver
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': title,
                },
            },
            Source=SENDER,
        )
    except ClientError as error:
        raise HTTPException(status_code=400, detail=error.response['Error']['Message']) from error


def ses_send_email_build(receiver: str, user_id: str, user_pw: str, app_url: str):
    """
    send email_build
    """
    client = boto3.client('ses', region_name="ap-northeast-2", aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    with open('utils/ses/email_build_template.html', 'r', encoding='UTF8') as email_format:
        body_html = email_format.read()
        email_format.close()
        body_html = body_html.replace('user_id', user_id)
        body_html = body_html.replace('user_pw', user_pw)
        body_html = body_html.replace('app_url', app_url)
    try:
        client.send_email(
            Destination={
                'ToAddresses': [
                    receiver,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': "웹앱팩토리 앱 빌드가 성공적으로 완료되었습니다.",
                },
            },
            Source=SENDER
        )

    except ClientError as error:
        print(error.response['Error']['Message'])
