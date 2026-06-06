# Word Count

Counts word frequencies in a text file or URL and reports the top K most frequent words.

## Usage

```bash
./word_count/word_count.py <file_or_url> [options]
```

### Arguments

| Argument | Description |
|---|---|
| `file` | Path to a text file or an `http`/`https` URL |
| `-k K`, `--top K` | Show the top K words by frequency (default: 20) |

### Examples

```bash
# Count words in a local file, show top 10
./word_count/word_count.py book.txt -k 10

# Count words from a URL
./word_count/word_count.py https://www.gutenberg.org/cache/epub/2489/pg2489.txt -k 20

# Verbose output
./word_count/word_count.py book.txt -k 10 -v
```

### Output

```
Top 5 words:
  the : 14550
  of  : 6694
  and : 6445
  a   : 4700
  to  : 4671
```

## Running tests

```bash
python -m unittest test_counter_dict test_word_count -v
```
