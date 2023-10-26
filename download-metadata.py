from multiprocessing.pool import ThreadPool
import os
import subprocess
import shutil
import jsonlines
from datetime import datetime, timedelta
from dotenv import dotenv_values
from internetarchive import get_session

THREAD_COUNT = 24
YESTERDAY = (datetime.today() - timedelta(5)).strftime("%Y-%m-%d")


def download_item(identifier, name):
    identifier.download(name)


config = dotenv_values(".env")

cookies = {
    "cookies": {
        "logged-in-user": config["logged-in-user"],
        "logged-in-sig": config["logged-in-sig"],
    }
}
s = get_session(config=cookies)
item = s.get_item((f"YT-VIDEO-METADATA-{YESTERDAY}"))
files = [(item, f"YT-VIDEO-METADATA-{YESTERDAY}-{i:02}.jsonl.gz") for i in range(0, 24)]
with ThreadPool(THREAD_COUNT) as pool:
    pool.starmap(download_item, files)

subprocess.call("./unzip.sh")

output_jsonl = []

if os.path.isfile(f"video-metadata-with-lang-{YESTERDAY}.jsonl"):
    os.remove(f"video-metadata-with-lang-{YESTERDAY}.jsonl")

for i in range(0, 24):
    with jsonlines.open(
        f"YT-VIDEO-METADATA-{YESTERDAY}/YT-VIDEO-METADATA-{YESTERDAY}-{i:02}.jsonl"
    ) as reader:
        with jsonlines.open(
            f"video-metadata-with-lang-{YESTERDAY}.jsonl", mode="a"
        ) as writer:
            writer.write_all(reader.iter())

shutil.rmtree(f"YT-VIDEO-METADATA-{YESTERDAY}")
