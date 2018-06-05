#!/usr/bin/env python3
import pymodm as modm
import pymongo as mongo
from app.models import User

def create_user(username, plaintext_password):
    new_user = User()
    new_user.username = username
    new_user.set_password(plaintext_password)
    try:
        new_user.save(force_insert=True)
    except mongo.errors.DuplicateKeyError as e:
        print(e)
        exit(1)

def change_password(username, new_plaintext_password):
    try:
        user = User.objects.get({'username':username})
    except User.DoesNotExist:
        print("User", username, "not found!")
        exit(1)
    user.set_password(new_plaintext_password)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Database operations for flask app with sqlalchemy database wrapper")
    parser.add_argument("--create-user", nargs=2, metavar=("USERNAME", "PASSWORD"), help="Create a user USERNAME with password PASSWORD")
    parser.add_argument("--change-password", nargs=2, metavar=("USERNAME", "PASSWORD"), help="Change user USERNAME's password to PASSWORD")
    args = parser.parse_args()
    if args.create_user:
        create_user(args.create_user[0], args.create_user[1])
    if args.change_password:
        change_password(args.change_password[0], args.change_password[1])
