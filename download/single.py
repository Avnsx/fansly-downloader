"""Single Post Downloading"""


from fileio.dedupe import dedupe_init
from .common import process_download_accessible_media
from .core import DownloadState
from .types import DownloadType

from config import FanslyConfig
from textio import input_enter_continue, print_error, print_info, print_warning
from utils.common import is_valid_post_id


def download_single_post(config: FanslyConfig, state: DownloadState):
    """Downloads a single post."""

    # This is important for directory creation later on.
    state.download_type = DownloadType.SINGLE

    print_info(f"You have launched in Single Post download mode.")

    if config.post_id is not None:
        print_info(f"Trying to download post {config.post_id} as specified on the command-line ...")
        post_id = config.post_id

    elif not config.interactive:
        raise RuntimeError(
            'Single Post downloading is not supported in non-interactive mode '
            'unless a post ID is specified via command-line.'
        )

    else:
        print_info(f"Please enter the ID of the post you would like to download."
            f"\n{17*' '}After you click on a post, it will show in your browsers URL bar."
        )
        print()
        
        while True:
            post_id = input(f"\n{17*' '}► Post ID: ")

            if is_valid_post_id(post_id):
                break

            else:
                print_error(f"The input string '{post_id}' can not be a valid post ID."
                    f"\n{22*' '}The last few numbers in the url is the post ID"
                    f"\n{22*' '}Example: 'https://fansly.com/post/1283998432982'"
                    f"\n{22*' '}In the example, '1283998432982' would be the post ID.",
                    17
                )

    post_response = config.http_session.get(
        'https://apiv3.fansly.com/api/v1/post',
        params={'ids': post_id, 'ngsw-bypass': 'true',},
        headers=config.http_headers()
    )

    if post_response.status_code == 200:
        # From: "accounts"
        creator_username, creator_display_name = None, None

        # post object contains: posts, aggregatedPosts, accountMediaBundles, accountMedia, accounts, tips, tipGoals, stories, polls
        post_object = post_response.json()['response']
        
        # if access to post content / post contains content
        if post_object['accountMedia']:

            # parse post creator name
            if creator_username is None:
                # the post creators reliable accountId
                state.creator_id = post_object['accountMedia'][0]['accountId']

                creator_display_name, creator_username = next(
                    (account.get('displayName'), account.get('username'))
                    for account in post_object.get('accounts', [])
                    if account.get('id') == state.creator_id
                )

                # Override the creator's name with the one from the posting.
                # Post ID could be from a different creator than specified
                # in the config file.
                state.creator_name = creator_username
    
                if creator_display_name and creator_username:
                    print_info(f"Inspecting a post by {creator_display_name} (@{creator_username})")
                else:
                    print_info(f"Inspecting a post by {creator_username.capitalize()}")

            # Deferred deduplication init because directory may have changed
            # depending on post creator (!= configured creator)    
            dedupe_init(config, state)

            process_download_accessible_media(config, state, post_object['accountMedia'], post_id)
        
        else:
            print_warning(f"Could not find any accessible content in the single post.")
    
    else:
        print_error(f"Failed single post download. Response code: {post_response.status_code}\n{post_response.text}", 20)
        input_enter_continue(config.interactive)
