"""
fs util
"""
import firebase_admin
from firebase_admin import credentials, firestore

from env import FIREBASE_INFO


def create_fs_session():
    """
    create fs session
    """
    try:
        cred = credentials.Certificate(FIREBASE_INFO)
        firebase_admin.initialize_app(cred)
        yield firestore.client()
    finally:
        firebase_admin.delete_app(firebase_admin.get_app())
