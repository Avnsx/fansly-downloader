"""Message Downloading"""


import random

from time import sleep

from .common import process_download_accessible_media
from .downloadstate import DownloadState
from .types import DownloadType

from config import FanslyConfig
from textio import input_enter_continue, print_error, print_info, print_warning


def download_messages(config: FanslyConfig, state: DownloadState):
    # This is important for directory creation later on.
    state.download_type = DownloadType.MESSAGES

    print_info(f"Initiating Messages procedure. Standby for results.")
    print()
    
    groups_response = config.http_session.get(
        'https://apiv3.fansly.com/api/v1/group',
        headers=config.http_headers()
    )

    if groups_response.status_code == 200:
        groups_response = groups_response.json()['response']['groups']

        # go through messages and check if we even have a chat history with the creator
        group_id = None

        for group in groups_response:
            for user in group['users']:
                if user['userId'] == state.creator_id:
                    group_id = group['id']
                    break

            if group_id:
                break

        # only if we do have a message ("group") with the creator
        if group_id:

            msg_cursor: str = '0'

            while True:

                params = {'groupId': group_id, 'limit': '25', 'ngsw-bypass': 'true'}

                if msg_cursor != '0':
                    params['before'] = msg_cursor

                messages_response = config.http_session.get(
                    'https://apiv3.fansly.com/api/v1/message',
                    headers=config.http_headers(),
                    params=params,
                )

                if messages_response.status_code == 200:
                
                    # post object contains: messages, accountMedia, accountMediaBundles, tips, tipGoals, stories
                    post_object = messages_response.json()['response']

                    process_download_accessible_media(config, state, post_object['accountMedia'])

                    # get next cursor
                    try:
                        # Fansly rate-limiting fix
                        # (don't know if messages were affected at all)
                        sleep(random.uniform(2, 4))
                        msg_cursor = post_object['messages'][-1]['id']

                    except IndexError:
                        break # break if end is reached

                else:
                    print_error(f"Failed messages download. messages_req failed with response code: {messages_response.status_code}\n{messages_response.text}", 30)

        elif group_id is None:
            print_warning(f"Could not find a chat history with {state.creator_name}; skipping messages download ...")

    else:
        print_error(f"Failed Messages download. Response code: {groups_response.status_code}\n{groups_response.text}", 31)
        input_enter_continue(config.interactive)
