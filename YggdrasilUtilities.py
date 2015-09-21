"""provides the methods documented here: http://wiki.vg/Authentication"""
import requests
import json


def login(username, password, client_token):
    url = 'https://authserver.mojang.com/authenticate'
    body = json.dumps(
        {"agent": {"name": "Minecraft", "version": 1}, "username": username, "password": password,
         "clientToken": client_token})
    header = {'Content-Type': 'application/json'}
    response = requests.post(url, data=body, headers=header)
    return response.json()

    # 400 {"error":"IllegalArgumentException","errorMessage":"Error saving token."}


def refresh(access_token, client_token):
    url = 'https://authserver.mojang.com/refresh'
    body = json.dumps({"accessToken": access_token, "clientToken": client_token})
    header = {'Content-Type': 'application/json'}
    response = requests.post(url, data=body, headers=header)
    return response.json()


def validate_access_token(access_token, client_token):
    url = 'https://authserver.mojang.com/validate'
    body = json.dumps({"accessToken": access_token, "clientToken": client_token})
    header = {'Content-Type': 'application/json'}
    response = requests.post(url, data=body, headers=header)
    return response
    # 204 = No Content, means tokens are correct
    # 403 = forbidden, invalid username/password


def sign_out(username, password):
    url = 'https://authserver.mojang.com/signout'
    body = json.dumps({"username": username, "password": password})
    header = {'Content-Type': 'application/json'}
    response = requests.post(url, data=body, headers=header)
    return response
    # 204 = No Content, means tokens are correct
    # 403 = forbidden, invalid username/password


def invalidate_access_token(access_token, client_token):
    url = 'https://authserver.mojang.com/invalidate'
    body = json.dumps({"accessToken": access_token, "clientToken": client_token})
    header = {'Content-Type': 'application/json'}
    response = requests.post(url, data=body, headers=header)
    return response
    # 204 = No Content, means tokens are correct
    # 403 = forbidden, invalid username/password


__author__ = 'azrad'
__version__ = '0.1'
