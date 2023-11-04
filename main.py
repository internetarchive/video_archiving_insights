#!/usr/bin/env python3

import hmac
import os
import time

from datetime import date, timedelta
from urllib.error import URLError
import requests
from wordcloud import WordCloud
from sumgram.sumgram import get_top_sumgrams
from langdetect import detect

import matplotlib.pyplot as plt
import altair as alt
import streamlit as st
import pandas as pd
import numpy as np

from download_metadata import main as download_metadata


TITLE = "Video Archiving Insights"
ICON = "data:image/png;base64,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"
# DATALOC = "file://localhost/data/"
DATALOC = ""
TOPCOUNT = 100

st.set_page_config(page_title=TITLE, page_icon=ICON)
st.title(TITLE)


def htime(dur):
    unit = "sec"
    if abs(dur) >= 3600:
        dur /= 3600
        unit = "hr"
    elif abs(dur) >= 60:
        dur /= 60
        unit = "min"
    return f"{dur:,.1f} {unit}"


def getlang(text):
    try:
        return detect(text)
    except:
        return None


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


@st.cache_data(show_spinner=False)
def load_local_data(day):
    fp = f"{DATALOC}video-metadata-with-lang-{day}.jsonl"
    # download metadata file
    if not os.path.isfile(fp):
        download_metadata(day)
    df = pd.read_json(fp, lines=True)
    # remove file because dataframe is cached by streamlit
    # os.remove(fp)
    if len(df) == 0:
        st.warning(f"No metadata available for the day: {day}")
        st.stop()
    df["categories"] = df["categories"].apply(lambda c: "+".join(c))
    return df


@st.cache_data
def get_tags(data, count=10):
    return (
        data["tags"]
        .explode("tags")
        .str.lower()
        .to_frame()
        .groupby("tags")["tags"]
        .agg(["count"])
        .sort_values("count", ascending=False)
        .head(count)
    )


@st.cache_data
def get_sumgrams(data, count=10, size=2):
    titles = [{"text": "\n".join(t)} for t in chunker(data["title"], 100)]
    top_sumgrams = [
        {sg["ngram"]: sg["term_freq"]}
        for sg in get_top_sumgrams(titles, size, params={"top_sumgram_count": count})[
            "top_sumgrams"
        ]
    ]
    return {k: v for s in top_sumgrams for k, v in s.items()}


day = st.date_input("Videos archived on", date.today() - timedelta(days=1))

with st.spinner("Preparing relevant metadata..."):
    try:
        data = load_local_data(day)
    except URLError as e:
        st.warning(
            f"Unable to show statistics because there is no metadata found for the day: {day}."
            "Please select a different day."
        )
        st.stop()

    vids = len(data)
    chan = len(pd.unique(data["uploader"]))
    tdur = data["duration"].sum()
    mdur = data["duration"].max()

    try:
        prev_day = day - timedelta(days=1)
        prev_data = load_local_data(prev_day)
        vids_diff = f"{vids-len(prev_data):,}"
        chan_diff = f"{chan-len(pd.unique(prev_data['uploader'])):,}"
        tdur_diff = htime(tdur - prev_data["duration"].sum())
        mdur_diff = htime(mdur - prev_data["duration"].max())
    except URLError as e:
        vids_diff = chan_diff = tdur_diff = mdur_diff = None

col1, col2, col3, col4 = st.columns(4)
col1.metric("Videos", f"{vids:,}", vids_diff)
col2.metric("Channels", f"{chan:,}", chan_diff)
col3.metric("Duration", htime(tdur), tdur_diff)
col4.metric("Longest", htime(mdur), mdur_diff, "inverse")

"## Lexical Highlights"

"### Top Tags"
tags_count = st.slider("Number of tags to show", 10, 100, 50, 10)
top_tags = get_tags(data, tags_count)
wc = WordCloud()
wc.generate_from_frequencies(top_tags.to_dict()["count"])
fig, ax = plt.subplots()
ax.imshow(wc)
ax.axis("off")
st.pyplot(fig)
with st.expander("See tags frequency"):
    st.table(top_tags)

# "### Top Title Sumgrams"
# sumgrams_count = st.slider("Number of sumgrams to show", 10, 100, 50, 10)
# sumgram_size = st.slider("Base sumgram size", 1, 10, 3)
# top_sumgrams_dict = get_sumgrams(data, sumgrams_count, sumgram_size)
# wc = WordCloud()
# wc.generate_from_frequencies(top_sumgrams_dict)
# fig, ax = plt.subplots()
# ax.imshow(wc)
# ax.axis("off")
# st.pyplot(fig)
# with st.expander("See sumgram frequency"):
#     st.table(
#         pd.DataFrame(
#             [(k, v) for k, v in top_sumgrams_dict.items()],
#             columns=["sumgram", "frequency"],
#         )
#     )

"### Languages"
c = (
    alt.Chart(data)
    .mark_bar()
    .encode(
        x="count(language):Q",
        y=alt.Y("language:N", sort="-x"),
        tooltip=["language", "count(language)"],
    )
)
st.altair_chart(c, use_container_width=True)

"## Video Duration"

"### Duration Histogram"
"Buckets: `0 sec`, `<1 min`, `<1 hr`, `>=1 hr`"
hist = np.histogram(
    data["duration"], bins=[0, 1, 60 - 1, 3600 - 1, data["duration"].max()]
)[0]
st.bar_chart(hist)

"### Duration Summary"
st.table(data["duration"].describe())

"### Cumulative Sorted Duration"
sdur = pd.DataFrame(
    {
        "videos": np.arange(vids) / vids * 100,
        "duration": data["duration"].sort_values(ascending=False) / tdur * 100,
    }
)
c = (
    alt.Chart(sdur)
    .mark_line()
    .transform_window(cumulative_duration="sum(duration)")
    .encode(x="videos:Q", y="cumulative_duration:Q")
)
st.altair_chart(c, use_container_width=True)

"### Top Longest Videos"
cols = st.columns(3)
for i, v in enumerate(data.nlargest(9, "duration").itertuples()):
    cols[i % 3].video(f"https://youtube.com/watch?v={v.id}")
    cols[i % 3].write(f"[{htime(v.duration)}]")

"## Category Duration"
cat_dur = data.groupby("categories")["duration"].agg(
    ["count", "sum", "mean", "min", "max"]
)
st.write(cat_dur)

"### Videos by Category"
st.bar_chart(cat_dur["count"])

"### Duration by Category"
st.bar_chart(cat_dur["sum"])

"### Mean Duration by Category"
st.bar_chart(cat_dur["mean"])

f"## Top {TOPCOUNT} Uploaders"
top_uploaders = (
    data.groupby(["uploader", "uploader"])["uploader"]
    .agg(["count"])
    .sort_values("count", ascending=False)
    .head(TOPCOUNT)
)
st.write(top_uploaders)

"## Miscellaneous"
with st.expander("Metadata sample"):
    st.write(data.head(10))
