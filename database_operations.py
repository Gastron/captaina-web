#!/usr/bin/env python3
import sqlalchemy
from app import db
from app.models import User

def initialise_db():
    db.create_all()

def create_user(username, plaintext_password):
    new_user = User(username=username, password=plaintext_password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        print(e)
        exit(1)

def change_password(username, new_plaintext_password):
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = new_plaintext_password
    else:
        print("User", username, "not found!")
        exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Database operations for flask app with sqlalchemy database wrapper")
    parser.add_argument("--init", action='store_true', help="Create the database based on defined models.")
    parser.add_argument("--create-user", nargs=2, metavar=("USERNAME", "PASSWORD"), help="Create a user USERNAME with password PASSWORD")
    parser.add_argument("--change-password", nargs=2, metavar=("USERNAME", "PASSWORD"), help="Change user USERNAME's password to PASSWORD")
    args = parser.parse_args()
    if args.init:
        initialise_db()
    if args.create_user:
        create_user(args.create_user[0], args.create_user[1])
    if args.change_password:
        change_password(args.change_password[0], args.change_password[1])
    
