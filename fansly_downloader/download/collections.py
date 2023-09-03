"""Download Fansly Collections"""


from .common import process_download_accessible_media
from .downloadstate import DownloadState
from .types import DownloadType

from fansly_downloader.config import FanslyConfig
from fansly_downloader.textio import input_enter_continue, print_error, print_info


def download_collections(config: FanslyConfig, state: DownloadState):
    """Downloads Fansly purchased item collections."""

    print_info(f"Starting Collections sequence. Buckle up and enjoy the ride!")

    # This is important for directory creation later on.
    state.download_type = DownloadType.COLLECTIONS

    # send a first request to get all available "accountMediaId" ids, which are basically media ids of every graphic listed on /collections
    collections_response = config.http_session.get(
        'https://apiv3.fansly.com/api/v1/account/media/orders/',
        params={'limit': '9999','offset': '0','ngsw-bypass': 'true'},
        headers=config.http_headers()
    )

    if collections_response.status_code == 200:
        collections_response = collections_response.json()
        
        # format all ids from /account/media/orders (collections)
        accountMediaIds = ','.join(
            [order['accountMediaId']
             for order in collections_response['response']['accountMediaOrders']]
        )
        
        # input them into /media?ids= to get all relevant information about each purchased media in a 2nd request
        post_object = config.http_session.get(
            f"https://apiv3.fansly.com/api/v1/account/media?ids={accountMediaIds}",
            headers=config.http_headers())

        post_object = post_object.json()
        
        process_download_accessible_media(config, state, post_object['response'])

    else:
        print_error(f"Failed Collections download. Response code: {collections_response.status_code}\n{collections_response.text}", 23)
        input_enter_continue(config.interactive)
