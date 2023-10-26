import requests
import json
class dx:
    def __init__(self):
        self.base_url=f'https://api.dispatch.eu.org/api/v2/'
        self.uname, self.password = None, None
    def ping(self, route: str, params: dict):
        url=self.base_url+route
        response=requests.get(url, params)
        return response.json()
    def new_user(self, uname: str, password: str):
        res=self.ping('/users/new', {"user": uname, "password": password})
        if "code" in res:
            match res["code"]:
                case 409:
                    return "already_exists"
                case 422:
                    return "bad_format"
                case _:
                    return "all_good"
        return "all_good"
    def login(self, uname: str, password: str):
        if self.ping(f'/user/{uname}/auth', {"password": password}):
            self.uname=uname
            self.password=password
            return "all_good"
        else:
            return "bad_credentials"
    def new_room(self, alias: str, users: str):
        res=self.ping("/rooms/create", {"alias": alias, "users": users, "user": self.uname, "password": self.password})
        if "code" in res:
            match res["code"]:
                case 422:
                    return "profanity"
                case 401:
                    return "bad_credentials"
                case _:
                    return "bad_response"
        else:
            return "all_good"
    def list_rooms(self):
        res=self.ping(f'/user/{self.uname}/rooms', {"password": self.password})
        if "code" in res:
            return "bad_credentials"
        else:
            return res
    def post(self, uuid, msg):
        res=self.ping(f'/rooms/{uuid}/post', {"user": self.uname, "password": self.password, "msg": msg})
        if "code" in res:
            match res["code"]:
                case 401:
                    return "bad_credentials"
                case 404:
                    return "no_such_room"
                case 422:
                    return "profanity"
                case 200:
                    return "success"
                case _:
                    return "bad_response"
        else:
            return "bad_response"
    def list_messages(self, uuid):
        res=self.ping(f'/rooms/{uuid}/messages', {"user":  self.uname, "password": self.password, "timestamp": 0})
        if "code" in res:
            match res["code"]:
                case 401:
                    return "bad_credentials"
                case 200:
                    return res
                case _:
                    return "bad_response"
        else:
            return "bad_response"
    def user_info(self, user):
        res=self.ping(f'/user/{user}', {})
        if "code" in res:
            match res["code"]:
                case 404:
                    return "no_such_user"
                case 200:
                    return res
                case _:
                    return "bad_response"
        else:
            return "bad_response"
