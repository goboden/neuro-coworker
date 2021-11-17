import argparse
import sys
import json
from typing import List, Dict
import telethon


text_types = ['bold', 'italic', 'underline', 'strikethrough', 'text_link']
sentences_separators = '.?!'


def parse_args():
    parser = argparse.ArgumentParser(description='Imports telegram chat from file.')
    parser.add_argument('input_file', help='Input file.')
    parser.add_argument('-i', dest='show_info', action='store_true', help='Show chat info.')
    parser.add_argument('-l', dest='show_users', action='store_true', help='Show user list.')
    parser.add_argument('-u', dest='user_id', help='Filter by user ID.')
    parser.add_argument('-of', dest='output_file', help='Output file.')
    args = parser.parse_args()
    return args


def read_chat_from_file(filename: str):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f'File "{filename}" not found.')


def get_chat_info(chat_dictionary: Dict) -> Dict:
    info = {info_key: chat_dictionary[info_key] for info_key in ['name', 'id']}
    # +++
    message_types = set()
    message_text_types = set()
    messages = chat_dictionary['messages']
    for message in messages:
        message_types.add(message['type'])
        if message['type'] == 'message' and isinstance(message['text'], List):
            for message_text_part in message['text']:
                if isinstance(message_text_part, Dict) and message_text_part['type'] not in text_types:
                    message_text_types.add(message_text_part['type'])
    info['message_types'] = message_types
    info['message_text_types'] = message_text_types
    return info


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


def message_to_string(message) -> str:
    msg = ''
    if isinstance(message, List):
        for part in message:
            if isinstance(part, str):
                msg += part
            elif isinstance(part, Dict) and part['type'] in text_types:
                msg += part['text']
            else:
                msg += ''
    else:
        msg = message
    return msg


def get_user_messages(chat_messages: Dict, user_id: str) -> List:
    user_messages = []
    for chat_message in chat_messages:
        if is_message(chat_message) and chat_message['from_id'] == user_id:
            user_messages.append(message_to_string(chat_message['text']))
    return user_messages


def prepare_message(message: str) -> [str, bool]:
    prepared = message.lstrip().rstrip()
    if len(prepared) == 0:
        return False
    prepared = ' '.join(prepared.splitlines())

    prepared = prepared.replace('т.к.', 'т_к_')

    return prepared


def try_to_split_message(message: str) -> List[str]:
    splited = [message]
    for separator in sentences_separators:
        iter_splited = []
        for msg in splited:
            splited_msg = msg.split(separator)
            for spl_part in splited_msg:
                prepared = prepare_message(spl_part)
                if prepared:
                    if prepared[-1] not in sentences_separators:
                        prepared += separator
                    iter_splited.append(prepared)
        splited = iter_splited

    return splited


def prepare_messages(messages: List[str]) -> List[str]:
    prepared_messages = []
    for message in messages:
        prepared_message = prepare_message(message)
        if prepared_message:
            splited = try_to_split_message(prepared_message)
            for spl in splited:
                prepared_messages.append(spl)
    return prepared_messages


def save_user_messages(filename: str, user_messages: List):
    prepared = prepare_messages(user_messages)
    with open(filename, 'w', encoding='utf-8') as f:
        for message in prepared:
            f.write(message + ' ')


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
            if args.output_file:
                save_user_messages(args.output_file, user_messages)
            else:
                print(f'User ID: {args.user_id}. Messages count {len(messages)}')
        else:
            print(f'No messages found for user "{args.user_id}"')


if __name__ == '__main__':
    main()
