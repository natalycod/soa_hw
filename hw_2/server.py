from concurrent import futures

import grpc
import mafia_pb2
import mafia_pb2_grpc
import random
import threading

from queue import Queue
from enum import Enum

NEED_USERS_COUNT = 4

current_sessions = {}

class MessageType(Enum):
    NONE = 1
    SERVER_MESSAGE = 2
    USER_MESSAGE = 3

class Message:
    def __init__(self):
        self._type = MessageType.NONE

    def make_server_message(self, text, is_major_type):
        self._type = MessageType.SERVER_MESSAGE
        self.text = text
        self.major_type = is_major_type
    
    def make_user_message(self, user_name, text, is_major_type):
        self._type = MessageType.USER_MESSAGE
        self.user_name = user_name
        self.text = text
        self.major_type = is_major_type

    def ConvertToGetMessageResponse(self):
        if self._type == MessageType.NONE:
            return mafia_pb2.GetMessageResponse(none_message=mafia_pb2.GetMessageResponse.NoneMessage())
        if self._type == MessageType.SERVER_MESSAGE:
            return mafia_pb2.GetMessageResponse(server_message=mafia_pb2.GetMessageResponse.ServerMessage(text=self.text, major_type=self.major_type))
        if self._type == MessageType.USER_MESSAGE:
            return mafia_pb2.GetMessageResponse(user_message=mafia_pb2.GetMessageResponse.UserMessage(user_name=self.user_name, text=self.text, major_type=self.major_type))

class Role(Enum):
    NONE = 'none'
    PEACEFUL = 'peaceful'
    MAFIA = 'mafia'
    COMISSAR = 'comissar'

class GameStage(Enum):
    NOT_STARTED = 'not_started'
    DAY = 'day'
    NIGHT = 'night'
    ENDED = 'ended'

class User:
    def __init__(self, name):
        self.name = name
        self.role = Role.NONE
        self.messages = Queue()
        self.ready_to_end_day = False
        self.ready_to_end_night = False
        self.blamed_anyone = False
        self.blamed_count = 0
        self.alive = True
        self.found_mafia = None
    
    def add_message(self, message):
        self.messages.put(message)
    
    def get_message(self):
        if self.messages.empty():
            return Message()
        return self.messages.get()

    def set_role(self, user_role):
        self.role = user_role
        message = Message()
        message.make_server_message("Your role is " + self.role.value, False)
        self.add_message(message)

class Session:
    def __init__(self):
        self.session_name = ""
        self.game_stage = GameStage.NOT_STARTED
        self.users = {}
        self.ready_to_end_day_count = 0
        self.ready_to_end_night_count = 0
        self.stage_messages = []

        threading.Thread(target=self._keep_relevant, daemon=False, args=[]).start()

    def _clear_stage(self):
        self.ready_to_end_day_count = 0
        self.ready_to_end_night_count = 0
        for name, user in self.users.items():
            user.ready_to_end_day = False
            user.ready_to_end_night = False
            user.blamed_count = 0
            user.blamed_anyone = False
            if not user.alive:
                user.ready_to_end_day = True
                user.ready_to_end_night = True
                self.ready_to_end_day_count += 1
                self.ready_to_end_night_count += 1
            elif user.role == Role.PEACEFUL:
                user.ready_to_end_night = True
                self.ready_to_end_night_count += 1

    def _send_stage_messages(self):
        for name, user in self.users.items():
            for stage_message in self.stage_messages:
                user.add_message(stage_message)
            alive_message = Message()
            alive_message.make_server_message("Living players: " + ", ".join(self._get_alive_players()), True)
            user.add_message(alive_message)
        self.stage_messages = []

    def _try_to_start_game(self):
        if len(self.users) < NEED_USERS_COUNT:
            return False
        self.game_stage = GameStage.DAY
        self._clear_stage()
        for name, user in self.users.items():
            message = Message()
            message.make_server_message("--- GAME STARTED ---", True)
            user.add_message(message)

        current_users = [_name for _name, _user in self.users.items()]
        random.shuffle(current_users)
        self.users[current_users[0]].set_role(Role.COMISSAR)
        self.users[current_users[1]].set_role(Role.MAFIA)
        for i in range(2, len(current_users)):
            self.users[current_users[i]].set_role(Role.PEACEFUL)
        return True

    def _blame_users(self):
        alive_players = self._get_alive_players()
        
        blamed_user = None
        cnt_alive = len(alive_players)
        for name, user in self.users.items():
            if user.blamed_count * 2 > cnt_alive:
                blamed_user = name
                break
        if blamed_user is None:
            return

        self.users[blamed_user].alive = False
        message = Message()
        message.make_server_message("User " + blamed_user + " was killed by the crowd", True)
        self.stage_messages.append(message)

    def _try_to_end_day(self):
        if self.ready_to_end_day_count < len(self.users):
            return False
        self._blame_users()
        self.game_stage = GameStage.NIGHT
        self._clear_stage()

        for name, user in self.users.items():
            message = Message()
            message.make_server_message("--- NIGHT TIME ---", True)
            user.add_message(message)

        self._send_stage_messages()

        for name, user in self.users.items():
            rules_message = Message()
            if user.role == Role.MAFIA:
                rules_message.make_server_message("You must kill somebody (\"kill\" and name of your victim)", False)
                user.add_message(rules_message)
            if user.role == Role.COMISSAR:
                rules_message.make_server_message("You must check somebody (\"check\" and name of your victim)", False)
                user.add_message(rules_message)
        return True

    def _try_to_end_night(self):
        if self.ready_to_end_night_count < len(self.users):
            return False
        self.game_stage = GameStage.DAY
        self._clear_stage()
        for name, user in self.users.items():
            message = Message()
            message.make_server_message("--- DAY TIME ---", True)
            user.add_message(message)
        self._send_stage_messages()
        return True

    def _try_to_end_game(self):
        if self.game_stage == GameStage.NOT_STARTED:
            return False
        mafia_cnt = 0
        peace_cnt = 0
        for name, user in self.users.items():
            if not user.alive:
                continue
            if user.role == Role.MAFIA:
                mafia_cnt += 1
            else:
                peace_cnt += 1
        
        main_message = Message()
        main_message.make_server_message("--- END ---", True)

        if mafia_cnt == 0:
            self.stage_messages.append(main_message)
            message = Message()
            message.make_server_message("Peace won!", True)
            self.stage_messages.append(message)
        elif mafia_cnt >= peace_cnt:
            self.stage_messages.append(main_message)
            message = Message()
            message.make_server_message("Mafia won!", True)
            self.stage_messages.append(message)
        else:
            return False
        self._send_stage_messages()
        return True

    def _keep_relevant(self):
        while True:
            if self._try_to_end_game():
                break
            if self.game_stage == GameStage.NOT_STARTED:
                self._try_to_start_game()
            if self.game_stage == GameStage.DAY:
                self._try_to_end_day()
            elif self.game_stage == GameStage.NIGHT:
                self._try_to_end_night()

    def add_user(self, user_name):
        self.users[user_name] = User(user_name)
        for name, user in self.users.items():
            connection_message = Message()
            current_users_message = Message()
            if (name == user_name):
                connection_message.make_server_message("You were succesfully connected!", False)
            else:
                connection_message.make_server_message("User " + user_name + " joined the session", True)
            current_users_message.make_server_message("Current users: " + ", ".join([_name for _name, _user in self.users.items()]), True)
            user.add_message(connection_message)
            user.add_message(current_users_message)

    def get_user_message(self, user_name):
        if user_name not in self.users:
            return Message()
        return self.users[user_name].get_message()
    
    def _get_alive_players(self):
        result = []
        for name, user in self.users.items():
            if user.alive:
                result.append(name)
        return result

    def end_day(self, user_name):
        if user_name not in self.users:
            return
        if not self.users[user_name].alive:
            return "It doesn't matter anymore, you're dead"
        if self.game_stage != GameStage.DAY:
            return "You can't end day, because it's not day now"
        if self.users[user_name].ready_to_end_day:
            return "You already told that you are ready to end the day"
        self.ready_to_end_day_count += 1
        self.users[user_name].ready_to_end_day = True

    def check(self, user_name, check_name):
        if not self.users[user_name].alive:
            return "You can't check anyone, you're dead"
        if self.game_stage != GameStage.NIGHT:
            return "You can check users only at night"
        if self.users[user_name].role != Role.COMISSAR:
            return "Only comissar can check users"
        if self.users[user_name].ready_to_end_night:
            return "You already checked someone this night! Wait for the next one"
        self.users[user_name].ready_to_end_night = True
        self.ready_to_end_night_count += 1
        message = Message()
        if self.users[check_name].role == Role.MAFIA:
            self.users[user_name].found_mafia = check_name
            message.make_server_message("Congrats! User " + check_name + " is mafia", False)
        else:
            message.make_server_message("Sorry! User " + check_name + " is not mafia. Try again next night", False)
        self.users[user_name].add_message(message)
    
    def kill(self, user_name, kill_name):
        if not self.users[user_name].alive:
            return "You can't kill anyone, you're dead"
        if not self.users[kill_name].alive:
            return "You can't kill this user, he's already dead"
        if self.game_stage != GameStage.NIGHT:
            return "You can kill users only at night"
        if self.users[user_name].role != Role.MAFIA:
            return "Only mafia can kill users"
        if self.users[user_name].ready_to_end_night:
            return "You already killed someone this night! Wait for the next one"
        self.users[user_name].ready_to_end_night = True
        self.ready_to_end_night_count += 1
        self.users[kill_name].alive = False
        message = Message()
        message.make_server_message("Fine! Consider " + kill_name + " dead", False)
        self.users[user_name].add_message(message)
        night_message = Message()
        night_message.make_server_message("User " + kill_name + " was killed last night", True)
        self.stage_messages.append(night_message)

    def send_chat_message(self, user_name, text):
        if not self.users[user_name].alive:
            return "You can't chat, you're dead"
        if self.game_stage == GameStage.NIGHT:
            return "You can't chat at night"
        for name, user in self.users.items():
            message = Message()
            if name == user_name:
                message.make_user_message(user_name, text, True)
            else:
                message.make_user_message(user_name, text, False)
            user.add_message(message)

    def publish(self, user_name):
        if not self.users[user_name].alive:
            return "You can't publish anything, you're dead"
        if self.game_stage != GameStage.DAY:
            return "You can publish your investigation only at day time"
        if self.users[user_name].role != Role.COMISSAR:
            return "Only comissar can post investigation"
        if self.users[user_name].found_mafia is None:
            return "You didn't find mafia yet, you can't publish investigation"
        for name, user in self.users.items():
            message = Message()
            if name == user_name:
                message.make_server_message("Comissar published his investigations. It seams that " + self.users[user_name].found_mafia + " is mafia!", False)
            else:
                message.make_server_message("Comissar published his investigations. It seams that " + self.users[user_name].found_mafia + " is mafia!", True)
            user.add_message(message)
    
    def blame(self, user_name, blame_name):
        if not self.users[user_name].alive:
            return "You can't blame anyone, you're dead"
        if self.game_stage != GameStage.DAY:
            return "You can blame users only at day time"
        if self.users[user_name].blamed_anyone:
            return "You already blamed someone this day. Wait for the next one"
        if not self.users[blame_name].alive:
            return "You can't blame dead user"
        self.users[user_name].blamed_anyone = True
        self.users[blame_name].blamed_count += 1

class MafiaConnection(mafia_pb2_grpc.MafiaServicer):
    def ConnectToServer(self, request, context):
        if request.session_name not in current_sessions:
            current_sessions[request.session_name] = Session()
        session = current_sessions[request.session_name]
        if request.user_name in current_sessions[request.session_name].users:
            return mafia_pb2.CommonServerResponse(common_error=mafia_pb2.CommonServerResponse.CommonError(error_text="User with name " + request.user_name + " already exists in session " + request.session_name))
        if current_sessions[request.session_name].game_stage != GameStage.NOT_STARTED:
            return mafia_pb2.CommonServerResponse(common_error=mafia_pb2.CommonServerResponse.CommonError(error_text="Session " + request.session_name + " already started, you can't connect to it."))

        session.add_user(request.user_name)
        return mafia_pb2.CommonServerResponse(empty_message=mafia_pb2.CommonServerResponse.EmptyMessage())

    def GetNewMessage(self, request, context):
        message = current_sessions[request.session_name].get_user_message(request.user_name)
        return message.ConvertToGetMessageResponse()

    def _HandleCommonResponse(self, func_resp):
        if func_resp is not None:
            return mafia_pb2.CommonServerResponse(common_error=mafia_pb2.CommonServerResponse.CommonError(error_text=func_resp))
        return mafia_pb2.CommonServerResponse(empty_message=mafia_pb2.CommonServerResponse.EmptyMessage())

    def CheckUser(self, request, context):
        resp = current_sessions[request.session_name].check(request.user_name, request.check_name)
        return self._HandleCommonResponse(resp)

    def KillUser(self, request, context):
        resp = current_sessions[request.session_name].kill(request.user_name, request.kill_name)
        return self._HandleCommonResponse(resp)

    def SendChatMessage(self, request, context):
        resp = current_sessions[request.session_name].send_chat_message(request.user_name, request.text)
        return self._HandleCommonResponse(resp)

    def EndDay(self, request, context):
        resp = current_sessions[request.session_name].end_day(request.user_name)
        return self._HandleCommonResponse(resp)

    def Publish(self, request, context):
        resp = current_sessions[request.session_name].publish(request.user_name)
        return self._HandleCommonResponse(resp)

    def Blame(self, request, context):
        resp = current_sessions[request.session_name].blame(request.user_name, request.blame_name)
        return self._HandleCommonResponse(resp)


port = "50051"
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
mafia_pb2_grpc.add_MafiaServicer_to_server(MafiaConnection(), server)
server.add_insecure_port("[::]:" + port)
server.start()
print("Server started, listening on " + port)
server.wait_for_termination()
