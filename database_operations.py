#!/usr/bin/env python3
from app import db

def createDB(confirm = True):
    confirmation = not confirm 
    if confirm:
        prompt = "Are you sure [y/N]? This will overwrite any existing data"
        confirmation = input(prompt).lower() == "y"
    if confirmation:
        db.create_all()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Database operations for flask app with sqlalchemy database wrapper")
    parser.add_argument("--init", action='store_true', help="Create the database based on defined models. Will overwrite any existing data")
    args = parser.parse_args()
    if args.init:
        createDB()
    
