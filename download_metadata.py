from multiprocessing.pool import ThreadPool
import os
import shutil
import gzip
import copy
from datetime import datetime, timedelta
import jsonlines
from dotenv import dotenv_values
from internetarchive import download as download_item

THREAD_COUNT = 12
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


def download_item_helper(identifier, filename):
    download_item(identifier, identifier+filename)


def main(date=YESTERDAY):
    # generate list of filenames and download in parallel
    filenames = [(f"YT-VIDEO-METADATA-{date}", f"-{i:02}.jsonl.gz") for i in range(0, 24)]
    with ThreadPool(THREAD_COUNT) as pool:
        pool.starmap(download_item_helper, filenames)

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
