"""
FCM 푸시 메시지
"""
import typing

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging


def send_push(title: str, body: str, fcm_token: str, cred: typing.Optional[dict] = None):
    """
    send FCM push message
    """
    cred = credentials.Certificate(cred if cred is not None else "google-account.json")
    app = firebase_admin.initialize_app(cred)

    messaging.send(messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=fcm_token
    ))
    firebase_admin.delete_app(app)
