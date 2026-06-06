import unittest
from counter_dict import _Dict, _MinHeap, CounterDict


# ─── _Dict ────────────────────────────────────────────────────────────────────

class TestDictAdd(unittest.TestCase):
    def test_set_and_get_single_key(self):
        d = _Dict()
        d["hello"] = 1
        self.assertEqual(d["hello"], 1)

    def test_set_multiple_keys(self):
        d = _Dict()
        d["a"] = 1
        d["b"] = 2
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)

    def test_keys_do_not_interfere(self):
        d = _Dict()
        d["x"] = 10
        d["y"] = 20
        self.assertEqual(d["x"], 10)


class TestDictUpdate(unittest.TestCase):
    def test_overwrite_existing_key(self):
        d = _Dict()
        d["hello"] = 1
        d["hello"] = 5
        self.assertEqual(d["hello"], 5)

    def test_overwrite_to_zero(self):
        d = _Dict()
        d["hello"] = 3
        d["hello"] = 0
        self.assertEqual(d["hello"], 0)


class TestDictRemove(unittest.TestCase):
    def test_delete_existing_key(self):
        d = _Dict()
        d["hello"] = 1
        del d["hello"]
        with self.assertRaises(KeyError):
            _ = d["hello"]

    def test_delete_missing_key_raises(self):
        d = _Dict()
        with self.assertRaises(KeyError):
            del d["missing"]


class TestDictEdgeCases(unittest.TestCase):
    def test_get_missing_key_raises(self):
        d = _Dict()
        with self.assertRaises(KeyError):
            _ = d["missing"]

    def test_set_then_delete_then_set_again(self):
        d = _Dict()
        d["hello"] = 1
        del d["hello"]
        d["hello"] = 99
        self.assertEqual(d["hello"], 99)

    def test_collision_keys_stored_independently(self):
        d = _Dict(bucket_count=1)  # force every key into the same bucket
        d["a"] = 1
        d["b"] = 2
        d["c"] = 3
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)
        self.assertEqual(d["c"], 3)

    def test_items_returns_all_entries(self):
        d = _Dict()
        d["a"] = 1
        d["b"] = 2
        self.assertEqual(sorted(d.items()), [("a", 1), ("b", 2)])


# ─── _MinHeap ─────────────────────────────────────────────────────────────────

class TestMinHeapPush(unittest.TestCase):
    def test_peek_after_single_push(self):
        h = _MinHeap()
        h.push(5)
        self.assertEqual(h.peek(), 5)

    def test_min_always_at_root_after_pushes(self):
        h = _MinHeap()
        for v in [30, 10, 50, 20, 40]:
            h.push(v)
        self.assertEqual(h.peek(), 10)

    def test_push_ascending_order(self):
        h = _MinHeap()
        for v in [1, 2, 3, 4, 5]:
            h.push(v)
        self.assertEqual(h.peek(), 1)

    def test_push_descending_order(self):
        h = _MinHeap()
        for v in [5, 4, 3, 2, 1]:
            h.push(v)
        self.assertEqual(h.peek(), 1)

    def test_len_increases_with_push(self):
        h = _MinHeap()
        for i in range(5):
            h.push(i)
            self.assertEqual(len(h), i + 1)


class TestMinHeapPop(unittest.TestCase):
    def test_pop_returns_minimum(self):
        h = _MinHeap()
        for v in [30, 10, 50, 20]:
            h.push(v)
        self.assertEqual(h.pop(), 10)

    def test_pop_reorders_so_next_min_is_at_root(self):
        h = _MinHeap()
        for v in [30, 10, 50, 20]:
            h.push(v)
        h.pop()
        self.assertEqual(h.peek(), 20)

    def test_pops_come_out_in_ascending_order(self):
        h = _MinHeap()
        for v in [30, 10, 50, 20, 40]:
            h.push(v)
        result = [h.pop() for _ in range(len(h))]
        self.assertEqual(result, sorted(result))

    def test_len_decreases_with_pop(self):
        h = _MinHeap()
        for v in [1, 2, 3]:
            h.push(v)
        h.pop()
        self.assertEqual(len(h), 2)


class TestMinHeapEdgeCases(unittest.TestCase):
    def test_peek_empty_raises(self):
        h = _MinHeap()
        with self.assertRaises(IndexError):
            h.peek()

    def test_pop_empty_raises(self):
        h = _MinHeap()
        with self.assertRaises(IndexError):
            h.pop()

    def test_push_then_pop_single_item(self):
        h = _MinHeap()
        h.push(42)
        self.assertEqual(h.pop(), 42)
        self.assertEqual(len(h), 0)

    def test_tuple_ordering(self):
        h = _MinHeap()
        h.push((50, "the"))
        h.push((10, "cat"))
        h.push((30, "a"))
        self.assertEqual(h.peek(), (10, "cat"))


# ─── CounterDict ──────────────────────────────────────────────────────────────

class TestCounterDictCount(unittest.TestCase):
    def test_count_single_word(self):
        c = CounterDict()
        c.count("hello")
        self.assertEqual(c.counts["hello"], 1)

    def test_count_same_word_increments(self):
        c = CounterDict()
        c.count("hello")
        c.count("hello")
        c.count("hello")
        self.assertEqual(c.counts["hello"], 3)

    def test_count_multiple_words_independently(self):
        c = CounterDict()
        c.count("cat")
        c.count("dog")
        c.count("cat")
        self.assertEqual(c.counts["cat"], 2)
        self.assertEqual(c.counts["dog"], 1)

    def test_count_none_raises(self):
        c = CounterDict()
        with self.assertRaises(ValueError):
            c.count(None)


class TestCounterDictTopK(unittest.TestCase):
    def setUp(self):
        self.c = CounterDict()
        for word, times in [("the", 10), ("a", 6), ("cat", 4), ("dog", 8), ("bird", 2)]:
            for _ in range(times):
                self.c.count(word)

    def test_top_k_returns_k_results(self):
        self.assertEqual(len(self.c.top_k(3)), 3)

    def test_top_k_correct_order(self):
        result = self.c.top_k(3)
        self.assertEqual(result[0], ("the", 10))
        self.assertEqual(result[1], ("dog", 8))
        self.assertEqual(result[2], ("a", 6))

    def test_top_k_larger_than_vocab_returns_all(self):
        result = self.c.top_k(100)
        self.assertEqual(len(result), 5)

    def test_top_k_zero_raises(self):
        with self.assertRaises(ValueError):
            self.c.top_k(0)

    def test_top_k_negative_raises(self):
        with self.assertRaises(ValueError):
            self.c.top_k(-1)

    def test_top_1_returns_most_frequent(self):
        result = self.c.top_k(1)
        self.assertEqual(result[0], ("the", 10))


if __name__ == "__main__":
    unittest.main()
