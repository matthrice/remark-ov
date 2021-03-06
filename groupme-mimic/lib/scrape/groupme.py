"""
groupme.py

Script to generate groupme history
Access token from: https://dev.groupme.com/
"""

import os
import time
import math

import requests
import requests_cache
from json import load

"""Install HTTP request cache"""
requests_cache.install_cache('groupme-cache')


def check_token(token):
    """
    Check the validity of the access token

    Params:
        @token - GroupMe API token
    Return:
        Bool indicating token validity
    """
    try:
        get_self_id(token)
        valid = True
    except:
        valid = False

    return valid


def get_url(token, chat_type, chat_ID, msg_limit):
    """
    Retrieve url for chat

    Params:
        @token - GroupMe API token
        @chat_type - group or direct
        @chat_id - GroupMe chat id
        @msg_limit - limit of messages per query (max 100)
    Return:
        URL for requesting chat
    """
    if chat_type == 'group':
        url = 'https://api.groupme.com/v3/groups/{}/messages'.format(chat_ID)
        url += "?token={}".format(token)
    elif chat_type == 'direct':
        url = 'https://api.groupme.com/v3/direct_messages'
        url += '?other_user_id={}'.format(chat_ID)
        url += "&token={}".format(token)

    url += "&limit={}".format(msg_limit)

    return url

def get_json(url):
    """
    Retrieve json from url

    Params:
        @url - url to send request
    Return:
        JSON object of response
    """
    try:
        res = requests.get(url=url)
    except requests.exceptions.HTTPError as e:
        return "Error: " + str(e)

    json = res.json()


    return json


def get_self_id(token):
    """
    Obtain a user's ID given token

    Params:
        @token - GroupMe API token
    Return:
        personal ID
    """
    url = "https://api.groupme.com/v3/users/me?token={}".format(token)
    json = get_json(url)
    user_id = json['response']['user_id']

    return user_id

def get_groups(token):
    """
    Return a list of group chats' IDs and names

    Params:
        @token - GroupMe API token
    Return:
        All group names
    """
    url = 'https://api.groupme.com/v3/groups?token={}'.format(token)
    json = get_json(url)
    response = json['response']

    groups = []
    for i in response:
        ID = i['id']
        name = i['name']
        groups.append([ID, name])

    return groups

def get_directs(token):
    """
    Return a list of direct message chats' IDs and names

    Params:
        @token - GroupMe API token
    Return:
        direct message chats
    """
    url = 'https://api.groupme.com/v3/chats?token={}'.format(token)
    json = get_json(url)
    response = json['response']

    directs = []
    for i in response:
        ID = i['other_user']['id']
        name = i['other_user']['name']
        directs.append([ID, name])

    return directs

def create_history(id, json, url, chat_type, chat_ID, msg_count, msg_limit):
    """Create a full chat history for a specific

    Params:
        @name - name of person
        @json - GroupMe API response in JSON format
        @url - URL being worked with
        @chat_type - the type of chat ('group' or 'direct')
        @chat_id - the chat's id
        @msg_count - total number of messages in the chat
    Return:
        Full history of a group chat as list
    """

    msg = ''
    if chat_type == 'group':
        msg = 'messages'
    elif chat_type == 'direct':
        msg = 'direct_messages'
    history = []


    num_messages = min(msg_count, len(json['response'][msg]))
    while num_messages > 0:
        if num_messages < msg_limit:
            msg_limit = num_messages % msg_limit

        for i in range(msg_limit):
            u_id = json['response'][msg][i]['user_id']
            if u_id == id:
                temp = {}
                temp['user_id'] = u_id
                temp['name'] = json['response'][msg][i]['name']
                text = json['response'][msg][i]['text']
                if text:
                    temp['text'] = text
                history.append(temp)
            num_messages -= 1

    return history



def write_single_history(path, name, full_history):
    """
    Records all text from an individual in a readable format

    Params:
        @path - path name to write to resources
        @name - name to write
        @full_history - all messages in list form
    """
    filename = os.path.join(path, '{}chathistory.txt'.format(name))
    filename = filename.replace(' ', '_')
    f = open(filename, 'w+')

    for message in full_history:
        if 'text' in message:
            text = message['text']
            text = clean_message(text)
            f.write(text)

    f.close()

def clean_message(text):
    """Clean text before creating history

    Params:
        @text - line of text to be cleaned
    Returns:
        clean text
    """
    text = text.replace('@', '') # remove @ symbols
    text = text.replace('*', '') # remove * symbols
    text = text.strip(' ')          # strip whitespace
    if text[-1] != '.' or text[-1] != '?' or text[-1] != '!':   # add period to end
        text += '.'
    text = ' ' + text     # add space to beginning
    return text

def scrape_history(token, group_id, user_id, user_name, path, message_count, message_limit):
    """Method to scrape for all user groupme history

    Params:
        @token: dev groupme token
        @group_id: groupme group id
        @user_id: groupme user_id
        @user_name: (no spaces) used for filenaming
        @path: directory for resulting .txt file
        @msg_count: desired number of messages to go through
        @msg_limit: set at 100

    """
    url = get_url(token, 'group', group_id, message_limit)
    i_json = get_json(url)
    history = create_history(user_id, i_json, url, 'group', group_id, message_count, message_limit)
    write_single_history(path, user_name, history)

def get_groupme_info(token, chat_name, user_name):
    """Returns chat_id, user_id info

    Params:
        @token: dev API token
        @chat_name: name of desired chat
        @user_name: name of desired user

    Return:
        chat_id and user_id
    """

    json = get_json('https://api.groupme.com/v3/groups?token={}'.format(token))
    chat_id = ''
    user_id = ''
    for chat in json['response']:
        if chat['name'] == chat_name:
            chat_id = chat['id']
            for member in chat['members']:
                if member['nickname'] == user_name:
                    user_id = member['user_id']
                    break
            break
    return chat_id, user_id
