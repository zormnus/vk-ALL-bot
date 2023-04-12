from bot_server import BotServer
from threading import Thread
from variables import api_token, group_id, name


def main():
    server = BotServer(api_token=api_token,
                       group_id=group_id,
                       server_name=name)
    Thread(target=server.start_listen).start()
    Thread(target=server.wait_next_day).start()


if __name__ == '__main__':
    main()
