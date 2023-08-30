"""Timeline Downloads"""


import traceback

from requests import Response
from time import sleep

from .common import process_download_accessible_media
from .core import DownloadState
from .types import DownloadType

from config import FanslyConfig
from errors import ApiError
from textio import input_enter_continue, print_debug, print_error, print_info, print_warning


def download_timeline(config: FanslyConfig, state: DownloadState) -> None:

    print_info(f"Executing Timeline functionality. Anticipate remarkable outcomes!")
    print()

    # This is important for directory creation later on.
    state.download_type = DownloadType.TIMELINE

    # this has to be up here so it doesn't get looped
    timeline_cursor = 0

    while True:
        if timeline_cursor == 0:
            print_info("Inspecting most recent Timeline cursor ...")

        else:
            print_info(f"Inspecting Timeline cursor: {timeline_cursor}")
    
        timeline_response = Response()

        # Simple attempt to deal with rate limiting
        for attempt in range(9999):
            try:
                # People with a high enough internet download speed & hardware specification will manage to hit a rate limit here
                endpoint = "timelinenew" if attempt == 0 else "timeline"

                if config.debug:
                    print_debug(f'HTTP headers: {config.http_headers()}')

                timeline_response = config.http_session.get(
                    f"https://apiv3.fansly.com/api/v1/{endpoint}/{state.creator_id}?before={timeline_cursor}&after=0&wallId=&contentSearch=&ngsw-bypass=true",
                    headers=config.http_headers()
                )

                break  # break if no errors happened; which means we will try parsing & downloading contents of that timeline_cursor

            except Exception:
                if attempt == 0:
                    continue

                elif attempt == 1:
                    print_warning(
                        f"Uhm, looks like we've hit a rate limit ..."
                        f"\n{20 * ' '}Using a VPN might fix this issue entirely."
                        f"\n{20 * ' '}Regardless, will now try to continue the download infinitely, every 15 seconds."
                        f"\n{20 * ' '}Let me know if this logic worked out at any point in time"
                        f"\n{20 * ' '}by opening an issue ticket, please!"
                    )
                    print('\n' + traceback.format_exc())

                else:
                    print(f"Attempt {attempt} ...")

                sleep(15)
    
        try:
            timeline_response.raise_for_status()

            if timeline_response.status_code == 200:

                post_object = timeline_response.json()['response']
        
                if config.debug:
                    print_debug(f'Post object: {post_object}')

                if not process_download_accessible_media(config, state, post_object['accountMedia']):
                    # Break on deduplication error - already downloaded
                    break

                print()

                # get next timeline_cursor
                try:
                    timeline_cursor = post_object['posts'][-1]['id']

                except IndexError:
                    # break the whole while loop, if end is reached
                    break

                except Exception:
                    message = \
                        'Please copy & paste this on GitHub > Issues & provide a short explanation (34):'\
                        f'\n{traceback.format_exc()}\n'

                    raise ApiError(message)

        except KeyError:
            print_error("Couldn't find any scrapable media at all!\
                \n This most likely happend because you're not following the creator, your authorisation token is wrong\
                \n or the creator is not providing unlocked content.",
                35
            )
            input_enter_continue(config.interactive)

        except Exception:
            print_error(f"Unexpected error during Timeline download: \n{traceback.format_exc()}", 36)
            input_enter_continue(config.interactive)

    # Check if atleast 20% of timeline was scraped; exluding the case when all the media was declined as duplicates
    low_yield = False

    if state.pic_count <= state.total_timeline_pictures * 0.2 and state.duplicate_count <= state.total_timeline_pictures * 0.2:
        print_warning(f"Low amount of Pictures scraped. Creators total Pictures: {state.total_timeline_pictures} | Downloaded: {state.pic_count}")
        low_yield = True
    
    if state.vid_count <= state.total_timeline_videos * 0.2 and state.duplicate_count <= state.total_timeline_videos * 0.2:
        print_warning(f"Low amount of Videos scraped. Creators total Videos: {state.total_timeline_videos} | Downloaded: {state.vid_count}")
        low_yield = True
    
    if low_yield:
        if not state.following:
            print(f"{20*' '}Follow the creator to be able to scrape media!")
        
        if not state.subscribed:
            print(f"{20*' '}Subscribe to the creator if you would like to get the entire content.")
        
        if not config.download_media_previews:
            print(f"{20*' '}Try setting download_media_previews to True in the config.ini file. Doing so, will help if the creator has marked all his content as previews.")

        print()
