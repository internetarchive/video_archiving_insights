from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import shutil
import gzip
import copy
from datetime import datetime, timedelta
import jsonlines
import streamlit as st
from internetarchive import get_item

THREAD_COUNT = 12
CONFIG_FILE = "./ia.ini"
YESTERDAY = (datetime.today() - timedelta(1)).strftime("%Y-%m-%d")
EXCLUDECOLS = [
    "upload_date",
    "channel_id",
    "view_count",
    "average_rating",
    "age_limit",
    "subtitles",
    "like_count",
    "automatic_captions",
]


def download_ia_metadata(item_id, filenames, date):
    """download of metadata"""
    ia_item = get_item(item_id, config_file=CONFIG_FILE)
    with ThreadPoolExecutor() as executor:
        progress_bar = st.progress(0)
        placeholder = st.empty()
        futures = [
            executor.submit(ia_item.download, filename, checksum=True)
            for filename in filenames
        ]
        # results = []
        for idx, future in enumerate(as_completed(futures), start=1):
            progress = idx / len(filenames)
            placeholder.text(f"Downloading {date} - {int(progress * 100)}%")
            # update progress bar
            progress_bar.progress(progress)
        progress_bar.empty()
        placeholder.empty()


def main(date=YESTERDAY):
    # generate list of filenames and download in parallel
    item_id = f"YT-VIDEO-METADATA-{date}"
    filenames = [f"{item_id}-{i:02}.jsonl.gz" for i in range(0, 24)]
    download_ia_metadata(item_id, filenames, date)

    # unzip files
    for i in range(0, 24):
        with gzip.open(
            f"YT-VIDEO-METADATA-{date}/YT-VIDEO-METADATA-{date}-{i:02}.jsonl.gz",
            "rb",
        ) as f_in:
            with open(
                f"YT-VIDEO-METADATA-{date}/YT-VIDEO-METADATA-{date}-{i:02}.jsonl",
                "wb",
            ) as f_out:
                shutil.copyfileobj(f_in, f_out)

    # remove file if already in place
    if os.path.isfile(f"video-metadata-with-lang-{date}.jsonl"):
        os.remove(f"video-metadata-with-lang-{date}.jsonl")

    # combine unzipped files into one .jsonl file
    for i in range(0, 24):
        with jsonlines.open(
            f"YT-VIDEO-METADATA-{date}/YT-VIDEO-METADATA-{date}-{i:02}.jsonl"
        ) as reader:
            with jsonlines.open(
                f"video-metadata-with-lang-{date}.jsonl", mode="a"
            ) as writer:
                # remove unused columns
                lines = copy.deepcopy(list(reader.iter()))
                for line in lines:
                    for col in EXCLUDECOLS:
                        del line[col]
                    writer.write(line)

    # remove downloaded files
    shutil.rmtree(f"YT-VIDEO-METADATA-{date}")


if __name__ == "__main__":
    main()
