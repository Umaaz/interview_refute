#!/usr/bin/env python3
import argparse
import atexit
import logging
import mimetypes
import os
import string
import tempfile
import urllib.error
import urllib.parse
import urllib.request

from counter_dict import CounterDict


def _is_url(source: str) -> bool:
    return urllib.parse.urlparse(source).scheme in ("http", "https")


def _has_binary_content(path: str) -> bool:
    with open(path, "rb") as f:
        return b"\x00" in f.read(1024)


def _download_to_temp(url: str) -> str:
    try:
        with urllib.request.urlopen(url) as response:
            suffix = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ""
            f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            logging.info(f"Downloading {url} to temporary file {f.name}")
            f.write(response.read())
            f.close()
            atexit.register(os.unlink, f.name)
            return f.name
    except urllib.error.URLError as e:
        raise argparse.ArgumentTypeError(f"Could not reach URL: {url} ({e.reason})")


def valid_text_file(path: str) -> str:
    if _is_url(path):
        path = _download_to_temp(path)
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"File not found: {path}")
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"Not a file: {path}")
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError(f"Permission denied: {path}")
    mime, _ = mimetypes.guess_type(path)
    if mime is not None and not mime.startswith("text/"):
        raise argparse.ArgumentTypeError(f"Not a text file: {path}")
    if mime is None and _has_binary_content(path):
        raise argparse.ArgumentTypeError(f"Not a text file: {path}")
    return path


def count_words(path: str) -> CounterDict:
    logging.info("Opening file: %s", path)
    with open(path, "r") as f:
        text = f.read()

    logging.info("Processing text content")
    counter_dict = CounterDict()
    for word in text.split():
        # strip trailing whitespace, and punctuation ("hello," becomes "hello")
        # note: this won't remove apostrophes in "don't" etc.
        strip = word.strip().strip(string.punctuation)
        if not strip:
            continue
        counter_dict.count(strip.lower())
    return counter_dict


def main():
    # set logging to info
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Count words in a text file.")
    parser.add_argument("file", type=valid_text_file, help="Path to a text file or URL")
    parser.add_argument(
        "-k", "--top", type=int, metavar="K", default=20, help="Show the top K words by frequency"
    )
    args = parser.parse_args()

    counts = count_words(args.file)

    if args.top:
        results = counts.top_k(args.top)
        width = max(len(word) for word, _ in results) if results else 0
        print(f"\nTop {args.top} words:")
        for word, freq in results:
            print(f"  {word:<{width}}: {freq}")


if __name__ == "__main__":
    main()
