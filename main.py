import request, re, time
from pyclr import *

from datetime import datetime


def printcallback(options: dict):
    i=0
    used=[]
    for key in options.keys():
        used.append(i)
        print(f"{i}: {key}")
        i+=1
    inp=input("Action #: ")
    try:
        inp=int(inp)
    except ValueError:
        print("Please enter a number")
        printcallback(options)
    if inp not in used:
        print("Please enter a valid choice")
        printcallback(options)
    else:
        key = list(options.keys())[inp]
        value = options[key]
        if isinstance(value,list):
            func=value[0]
            args=value[1]
            func(*args)
        else:
            value()
        
def formatlist(input_list, element_to_remove=None):
    items = [str(item).strip() for item in input_list if item != element_to_remove]
    return ', '.join(items[:-1]) + ', and ' + items[-1] if len(items) > 1 else items[0]


def relative_time(date_float):
    date = datetime.fromtimestamp(date_float)
    now = datetime.now()
    delta = now - date

    day = delta.days
    year, day = divmod(day, 365)
    month, day = divmod(day, 30)
    hour, second = divmod(delta.seconds, 3600)
    minute, second = divmod(second, 60)

    periods = [('year', year), ('month', month), ('day', day), ('hour', hour), ('minute', minute), ('second', second)]

    for period, value in periods:
        if value > 0:
            return f'{value} {period} ago' if value == 1 else f'{value} {period}s ago'

    return "just now"

class bold:
    def print(msg):
        print(f"\033[1;94m{msg}\033[0m")
class ui:
    def __init__(self):
        self.conn=request.dx()
    def login(self):
        bold.print("login")
        username=str(input("Username: "))
        passw=str(input("Password: "))
        res=self.conn.login(username, passw)
        if res=="bad_credentials":
            red.print("Wrong username or password")
            self.login()
        else:
            green.print(f"Logged in as {username}")
    def new_user(self):
        bold.print("signup")
        username=str(input("Username: "))
        password1=str(input("Password: "))
        password2=str(input("Please re-enter password: "))
        if password1!=password2:
            print("Passwords do not match")
        elif password2=="":
            print("Please ensure password is not empty")
        elif " " in username:
            red.print("Username cannot contains spaces")
        else:
            res=self.conn.new_user(username, password2)
            match res:
                case "bad_format":
                    red.print("Username must not start with a number, must be 3 or more characters long, and cannot contain any expletives ")
                    self.new_user()
                case "already_exists":
                    red.print(f"Username {username} is taken")
                    self.new_user()
                case "all_good":
                    green.print(f"Success!")
                    self.login()
    def new_room(self):
        bold.print("new room")
        alias=str(input("Please enter the name of your new room: "))
        users=str(input("Please enter the members of your room, seperated by commas: "))
        if not re.compile(r'^(\w+)(,\s*\w+)*$').match(users):
            print("Please ensure that the values are comma seperated")
            self.new_room()
        res=self.conn.new_room(alias, users)
        match res:
            case "profanity":
                print("No expletives")
                self.new_room()
            case "bad_credentials":
                orange.print("Sorry, could you login again?")
                self.login()
            case "all_good":
                print("Room created")
    def go_to_room(self):
        bold.print("list rooms")
        res=self.conn.list_rooms()
        if res=="bad_credentials":
            orange.print("Sorry, could you login again?")
            self.login()
        else:
            options={}
            options["exit this menu"]=[printcallback,[{
                                        "new room": self.new_room,
                                        "list rooms": self.go_to_room,
                                        "get info on a user": self.get_user_info
                                    }]]
            for room in (res):
                options[room["alias"]]=[self.switch_to_room, [room]]
            printcallback(options)

    def switch_to_room(self, room):
        bold.print(f"{room['alias']}")
        print(f"{room['alias']}'s members are: {formatlist(room['members'],self.conn.uname)}")
        while True:
            printcallback({
                "post": [self.post, [room]],
                "messages": [self.messages, [room]],
                "exit this menu": self.go_to_room
            })
    def post(self, room):
        bold.print("post")
        msg=str(input("Please enter your message (no profanity): "))
        res=self.conn.post(room["uuid"], msg)
        match res:
            case "bad_credentials":
                orange.print("Sorry, could you login again?")
                self.login()
            case "no_such_room":
                orange.print("Sorry, we couldn't find that room")
            case "profanity":
                red.print("No profanity please")
                self.post(room)
            case "bad_response":
                orangered.print("An error occurred on our end (likely http 500)")
            case "success":
                green.print("Message successfully posted")
    def messages(self, room):
        bold.print("list messages")
        res=self.conn.list_messages(room["uuid"])
        match res:
            case "bad_credentials":
                orange.print("Sorry, could you login again?")
                self.login()
            case "bad_response":
                orangered.print("An error occurred on our end (likely http 500)")
            case _:
                if type(res)==dict:
                    for message in res["content"]:
                        print(f"{message['sender']}, {relative_time(int(message['sent']))} - {message['content']}")
    def get_user_info(self):
        bold.print("get user info")
        user=str(input("Please enter the user who you want data on: "))
        res=self.conn.user_info(user)
        match res:
            case "bad_response":
                orangered.print("An error occurred on our end (likely http 500)")
            case "no_such_user":
                red.print("There is no such user")
            case _:
                if type(res)==dict:
                    print(f"User {res['username']} joined Dispatchx {relative_time(int(res['joined']))}. They {'are' if res['admin']==True else 'are not'} an admin. Their status is '{res['status']}'.")

    def set_status(self):
        bold.print("set status")
        status=str(input("Please input a status (no profanity please): "))
        res=self.conn.set_status(status)
        match res:
            case "bad_response":
                orangered.print("An error occurred on our end (likely http 500)")
            case "profanity":
                red.print("No profanity please")
                self.set_status()
            case "all_good":
                green.print("All good!")
try:
    main=ui()
    printcallback({
        "login": main.login,
        "signup": main.new_user
    })
    while True:
        printcallback({
            "new room": main.new_room,
            "list rooms": main.go_to_room,
            "get info on a user": main.get_user_info,
            "set my status": main.set_status
        })
except KeyboardInterrupt:
    exit(130)