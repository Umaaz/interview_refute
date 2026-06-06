import os
import tempfile
import unittest

from word_count import count_words


def make_temp_file(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestCountWordsBasic(unittest.TestCase):
    def test_single_word(self):
        path = make_temp_file("hello")
        result = count_words(path)
        self.assertEqual(result.counts["hello"], 1)
        os.unlink(path)

    def test_multiple_words(self):
        path = make_temp_file("the cat sat on the mat")
        result = count_words(path)
        self.assertEqual(result.counts["the"], 2)
        self.assertEqual(result.counts["cat"], 1)
        os.unlink(path)

    def test_case_insensitive(self):
        path = make_temp_file("The the THE")
        result = count_words(path)
        self.assertEqual(result.counts["the"], 3)
        os.unlink(path)

    def test_words_across_multiple_lines(self):
        path = make_temp_file("hello\nworld\nhello")
        result = count_words(path)
        self.assertEqual(result.counts["hello"], 2)
        self.assertEqual(result.counts["world"], 1)
        os.unlink(path)


class TestCountWordsEdgeCases(unittest.TestCase):
    def test_empty_file(self):
        path = make_temp_file("")
        result = count_words(path)
        self.assertEqual(result.top_k(10), [])
        os.unlink(path)

    def test_whitespace_only(self):
        path = make_temp_file("     \n\t\n   ")
        result = count_words(path)
        self.assertEqual(result.top_k(10), [])
        os.unlink(path)

    def test_multiple_spaces_between_words(self):
        path = make_temp_file("hello     world")
        result = count_words(path)
        self.assertEqual(result.counts["hello"], 1)
        self.assertEqual(result.counts["world"], 1)
        os.unlink(path)

    def test_punctuation_stripped_from_edges(self):
        path = make_temp_file("hello, hello")
        result = count_words(path)
        self.assertEqual(result.counts["hello"], 2)
        os.unlink(path)

    def test_internal_punctuation_preserved(self):
        # apostrophes inside a word are kept — "don't" stays "don't"
        path = make_temp_file("don't don't")
        result = count_words(path)
        self.assertEqual(result.counts["don't"], 2)
        os.unlink(path)

    def test_punctuation_only_token_ignored(self):
        path = make_temp_file("hello --- world")
        result = count_words(path)
        self.assertEqual(result.counts["hello"], 1)
        self.assertEqual(result.counts["world"], 1)
        with self.assertRaises(KeyError):
            _ = result.counts["---"]
        os.unlink(path)

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            count_words("/tmp/does_not_exist_xyz.txt")


class TestCountWordsTopK(unittest.TestCase):
    def setUp(self):
        self.path = make_temp_file(
            "the the the cat cat dog bird bird bird bird"
        )

    def tearDown(self):
        os.unlink(self.path)

    def test_top_1(self):
        result = count_words(self.path)
        self.assertEqual(result.top_k(1)[0], ("bird", 4))

    def test_top_k_order(self):
        result = count_words(self.path)
        words = [w for w, _ in result.top_k(3)]
        self.assertEqual(words, ["bird", "the", "cat"])

    def test_top_k_larger_than_vocab(self):
        result = count_words(self.path)
        self.assertEqual(len(result.top_k(100)), 4)


if __name__ == "__main__":
    unittest.main()
