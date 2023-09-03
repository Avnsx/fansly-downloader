"""Handles M3U8 Media"""


import av
import concurrent.futures
import io
import m3u8

from m3u8 import M3U8
from pathlib import Path
from rich.table import Column
from rich.progress import BarColumn, TextColumn, Progress

from fansly_downloader.config.fanslyconfig import FanslyConfig
from fansly_downloader.textio import print_error


def download_m3u8(config: FanslyConfig, m3u8_url: str, save_path: Path) -> bool:
    """Download M3U8 content as MP4.
    
    :param FanslyConfig config: The downloader configuration.
    :param str m3u8_url: The URL string of the M3U8 to download.
    :param Path save_path: The suggested file to save the video to.
        This will be changed to MP4 (.mp4).

    :return: True if successful or False otherwise.
    :rtype: bool
    """
    # parse m3u8_url for required strings
    parsed_url = {k: v for k, v in [s.split('=') for s in m3u8_url.split('?')[-1].split('&')]}

    policy = parsed_url.get('Policy')
    key_pair_id = parsed_url.get('Key-Pair-Id')
    signature = parsed_url.get('Signature')
    # re-construct original .m3u8 base link
    m3u8_url = m3u8_url.split('.m3u8')[0] + '.m3u8'
    # used for constructing .ts chunk links
    split_m3u8_url = m3u8_url.rsplit('/', 1)[0]
    #  remove file extension (.m3u8) from save_path
    save_path = save_path.parent / save_path.stem

    cookies = {
        'CloudFront-Key-Pair-Id': key_pair_id,
        'CloudFront-Policy': policy,
        'CloudFront-Signature': signature,
    }

    # download the m3u8 playlist
    playlist_content_req = config.http_session.get(m3u8_url, headers=config.http_headers(), cookies=cookies)

    if playlist_content_req.status_code != 200:
        print_error(f'Failed downloading m3u8; at playlist_content request. Response code: {playlist_content_req.status_code}\n{playlist_content_req.text}', 12)
        return False

    playlist_content = playlist_content_req.text

    # parse the m3u8 playlist content using the m3u8 library
    playlist_obj: M3U8 = m3u8.loads(playlist_content)

    # get a list of all the .ts files in the playlist
    ts_files = [segment.uri for segment in playlist_obj.segments if segment.uri.endswith('.ts')]

    # define a nested function to download a single .ts file and return the content
    def download_ts(ts_file: str):
        ts_url = f"{split_m3u8_url}/{ts_file}"
        ts_response = config.http_session.get(ts_url, headers=config.http_headers(), cookies=cookies, stream=True)
        buffer = io.BytesIO()

        for chunk in ts_response.iter_content(chunk_size=1024):
            buffer.write(chunk)

        ts_content = buffer.getvalue()

        return ts_content

    # if m3u8 seems like it might be bigger in total file size; display loading bar
    text_column = TextColumn(f"", table_column=Column(ratio=1))
    bar_column = BarColumn(bar_width=60, table_column=Column(ratio=5))

    disable_loading_bar = False if len(ts_files) > 15 else True

    progress = Progress(text_column, bar_column, expand=True, transient=True, disable = disable_loading_bar)

    with progress:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            ts_contents = [
                file for file in progress.track(
                    executor.map(download_ts, ts_files),
                    total=len(ts_files)
                )
            ]
    
    segment = bytearray()

    for ts_content in ts_contents:
        segment += ts_content
    
    input_container = av.open(io.BytesIO(segment), format='mpegts')

    video_stream = input_container.streams.video[0]
    audio_stream = input_container.streams.audio[0]

    # define output container and streams
    output_container = av.open(f"{save_path}.mp4", 'w') # add .mp4 file extension

    video_stream = output_container.add_stream(template=video_stream)
    audio_stream = output_container.add_stream(template=audio_stream)

    start_pts = None

    for packet in input_container.demux():
        if packet.dts is None:
            continue

        if start_pts is None:
            start_pts = packet.pts

        packet.pts -= start_pts
        packet.dts -= start_pts

        if packet.stream == input_container.streams.video[0]:
            packet.stream = video_stream

        elif packet.stream == input_container.streams.audio[0]:
            packet.stream = audio_stream

        output_container.mux(packet)

    # close containers
    input_container.close()
    output_container.close()

    return True
