import argparse
import sys
import json
from typing import List, Dict
import telethon


# python importer.py .\data\work_chat.json


def parse_args():
    parser = argparse.ArgumentParser(description='Imports telegram chat from file.')
    parser.add_argument('input_file')
    parser.add_argument('-i', dest='show_info', action='store_true', help='Show chat info.')
    parser.add_argument('-l', dest='show_users', action='store_true', help='Show user list.')
    parser.add_argument('-u', dest='user_id')
    args = parser.parse_args()
    return args


def read_chat_from_file(filename: str):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f'File "{filename}" not found.')


def get_chat_info(chat_dictionary: Dict) -> Dict:
    return {info_key: chat_dictionary[info_key] for info_key in ['name', 'id']}


def is_message(chat_message: Dict) -> bool:
    message_type = chat_message.get('type')
    return message_type == 'message'


def get_users_from_messages(chat_messages: Dict) -> Dict:
    chat_users = {}
    for chat_message in chat_messages:
        if is_message(chat_message):
            chat_users[chat_message['from_id']] = chat_message['from']
    return chat_users


def show_info(chat_info, messages):
    print(f'Chat: {chat_info}')
    print(f'Messages: {len(messages)}')


def show_users(chat_messages: Dict):
    print('Users:')
    users = get_users_from_messages(chat_messages)
    users_sorted = {key: value for key, value in users.items()}
    for num, key in enumerate(users_sorted):
        print(f'{num + 1}. {users[key]} ({key})')


def get_user_messages(chat_messages, user_id) -> List:
    user_messages = []
    for chat_message in chat_messages:
        if is_message(chat_message) and chat_message['from_id'] == user_id:
            user_messages.append(chat_message['text'])
    return user_messages


def save_user_messages(user_messages: List):
    pass


def main():
    args = parse_args()

    chat = read_chat_from_file(args.input_file)
    if not chat:
        sys.exit(0)

    chat_info = get_chat_info(chat)
    messages = chat['messages']

    if args.show_info:
        show_info(chat_info, messages)

    if args.show_users:
        show_users(messages)

    if args.user_id:
        user_messages = get_user_messages(messages, args.user_id)
        if len(user_messages) > 0:
            save_user_messages(user_messages)
        else:
            print(f'No messages found for user "{args.user_id}"')


if __name__ == '__main__':
    main()
