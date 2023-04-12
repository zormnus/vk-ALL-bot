import vk_api.vk_api
from vk_api.upload import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from threading import Lock

import datetime
import time

class BotServer(object):
    def __init__(self, api_token: str, group_id: int, server_name: str='None') -> None:
        self.server_name = server_name
        
        self.vk_session = vk_api.VkApi(token=api_token)

        self.longpoll = VkBotLongPoll(self.vk_session, group_id)

        self.vk = self.vk_session.get_api()

        self.vk_uploader = VkUpload(self.vk_session)

        self.all_counter = {}

        self.locker = Lock()

        self.perDay_all_limit = 3

        self.chats_database = {}

        self.amnesty_hour = 22

        self.amnesty_minute = 0


    def send_message_to_chat(self, chat_id:int, message:str):
        self.vk_session.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id': get_random_id()})


    def send_message_to_user(self, user_id:int, message:str):
        self.vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': get_random_id()})


    def upload_photo(self, url):
        photo = self.vk_uploader.photo_messages(photos=url)[0]
        return photo['owner_id'], photo['id']
    

    def send_pic_to_chat(self, url, chat_id, text=None):
        owner_id, photo_id = self.upload_photo(url)
        attachment = f'photo{owner_id}_{photo_id}'
        self.vk_session.method('messages.send', {'chat_id': chat_id, 'attachment': attachment, 'random_id': get_random_id(), 'message': text})

    

    def get_chat_members_data(self, chat_id):
        return self.vk_session.method('messages.getConversationMembers', {'peer_id': 2000000000 + chat_id})


    def start_listen(self):
        print('---------------------------------Listening the events---------------------------------')
        for event in self.longpoll.listen():
            print(event)
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
                user_id = event.message.from_id
                chat_id = event.chat_id
                
                if chat_id not in self.chats_database:
                        self.chats_database[chat_id] = self.get_chat_members_data(chat_id)

                if chat_id not in self.all_counter:
                    self.all_counter[chat_id] = {}
                    for item in self.chats_database[chat_id]['items']:
                        self.all_counter[chat_id][item['member_id']] = 0
                
                print(self.all_counter)
                try:
                    invite_action = event.message.action['type']
                except:
                    invite_action = ''
                    
                    
                if invite_action == 'chat_invite_user':
                    self.send_pic_to_chat(url='./res/helloWorld.jpg', chat_id=chat_id, text='ЙОУ!!!!!\nРады приветствовать тебя в трахать? драть? ДРАХАТЬ!!!\nА особенно он')
                    self.chats_database[chat_id].clear()
                    self.chats_database[chat_id] = self.get_chat_members_data(chat_id)


                if '@all' in event.obj.message['text'].lower() or '@все' in event.obj.message['text'].lower():
                    if user_id not in self.all_counter[chat_id]:
                        self.all_counter[chat_id][user_id] = 0
                    self.all_counter[chat_id][user_id] += 1

                    for person_dict in self.chats_database[chat_id]['items']:
                        if person_dict['member_id'] == user_id:
                            try:
                                admin_status = person_dict['is_admin']
                            except KeyError as kerr:
                                admin_status = False
                    if self.perDay_all_limit - self.all_counter[chat_id][user_id] > 0 and not admin_status:
                        self.send_message_to_chat(chat_id=chat_id, 
                                                message=f'Дружище, до кика из этой беседы осталось {self.perDay_all_limit - self.all_counter[chat_id][user_id]} олла))')

                    if self.all_counter[chat_id][user_id] >= self.perDay_all_limit and not admin_status:
                        self.send_pic_to_chat(url='./res/finishHIM.jpg', chat_id=chat_id)
                        self.vk.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
                        self.all_counter[chat_id][user_id] = 0
                        
                        
    def wait_next_day(self):
        while True:
            if datetime.datetime.now().hour == self.amnesty_hour \
                and datetime.datetime.now().minute == self.amnesty_minute:
                self.all_counter.clear()
                for chat_id in self.chats_database:
                    self.send_message_to_chat(chat_id=chat_id, message='Борьба за выживание продолжается ^_^\nУ всех по 3 олла!')
                time.sleep(60)
