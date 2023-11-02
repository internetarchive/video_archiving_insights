from multiprocessing.pool import ThreadPool
import os
import shutil
import gzip
import copy
from datetime import datetime, timedelta
import jsonlines
from dotenv import dotenv_values
from internetarchive import get_session

THREAD_COUNT = 24
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


def download_item(identifier, name):
    identifier.download(name)


def main(date=YESTERDAY):
    config = dotenv_values(".env")

    cookies = {
        "cookies": {
            "logged-in-user": config["logged-in-user"],
            "logged-in-sig": config["logged-in-sig"],
        }
    }
    s = get_session(config=cookies)
    item = s.get_item((f"YT-VIDEO-METADATA-{date}"))
    files = [(item, f"YT-VIDEO-METADATA-{date}-{i:02}.jsonl.gz") for i in range(0, 24)]
    with ThreadPool(THREAD_COUNT) as pool:
        pool.starmap(download_item, files)

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

    if os.path.isfile(f"video-metadata-with-lang-{date}.jsonl"):
        os.remove(f"video-metadata-with-lang-{date}.jsonl")

    for i in range(0, 24):
        with jsonlines.open(
            f"YT-VIDEO-METADATA-{date}/YT-VIDEO-METADATA-{date}-{i:02}.jsonl"
        ) as reader:
            with jsonlines.open(
                f"video-metadata-with-lang-{date}.jsonl", mode="a"
            ) as writer:
                lines = copy.deepcopy(list(reader.iter()))
                for line in lines:
                    for col in EXCLUDECOLS:
                        del line[col]
                    writer.write(line)

    shutil.rmtree(f"YT-VIDEO-METADATA-{date}")


if __name__ == "__main__":
    main()
