# Test file with intentional issues to trigger code review rules
import os
import sys
import json  # unused import

API_KEY = "sk-abcdefghijklmnopqrstuvwxyz123456789012345678"  # R001: hardcoded secret
password = "supersecret123"  # R001: hardcoded password

def getUserData():  # R008: camelCase
    try:
        result = os.system("ls -la")  # R010: os.system
        print("got data")  # R003: print statement
        return result
    except:  # R002: bare except
        pass

def badQuery(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # R006: f-string SQL
    return query

# TODO: fix this later  # R005: TODO comment
