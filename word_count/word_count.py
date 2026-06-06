#!/usr/bin/env python3
import argparse
import logging
import mimetypes
import os
import string
import urllib.parse
import urllib.request

from counter_dict import CounterDict


def _is_url(source: str) -> bool:
    return urllib.parse.urlparse(source).scheme in ("http", "https")


def _has_binary_content(path: str) -> bool:
    with open(path, "rb") as f:
        return b"\x00" in f.read(1024)


def valid_text_file(path: str) -> str:
    if _is_url(path):
        return path
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


def count_words(source: str) -> CounterDict:
    if _is_url(source):
        logging.info("Fetching URL: %s", source)
        with urllib.request.urlopen(source) as response:
            text = response.read().decode("utf-8")
    else:
        logging.info("Opening file: %s", source)
        with open(source, "r") as f:
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
    parser = argparse.ArgumentParser(description="Count words in a text file.")
    parser.add_argument("file", type=valid_text_file, help="Path to the text file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "-k", "--top", type=int, metavar="K", default=20, help="Show the top K words by frequency"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    counts = count_words(args.file)

    if args.top:
        results = counts.top_k(args.top)
        width = max(len(word) for word, _ in results) if results else 0
        print(f"\nTop {args.top} words:")
        for word, freq in results:
            print(f"  {word:<{width}}: {freq}")


if __name__ == "__main__":
    main()
