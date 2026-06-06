
_DEFAULT_BUCKET_COUNT = 64


class _Dict[K: str, V]:
    """
    A simple dictionary implementation with fixed-size buckets for collision resolution.

    Ideally this would have auto bucket resize, but for this example we are sticking with fixed size buckets.
    """
    def __init__(self, bucket_count: int = _DEFAULT_BUCKET_COUNT) -> None:
        self.__bucket_count: int = bucket_count
        self.__buckets: list[list[tuple[K, V]]] = [[] for _ in range(bucket_count)]

    def _hash(self, key: K) -> int:
        h = 0
        for ch in key:
            h = h * 31 + ord(ch)
        return h % self.__bucket_count

    def __getitem__(self, key: K) -> V:
        bucket = self.__buckets[self._hash(key)]
        for k, v in bucket:
            if k == key:
                return v
        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        bucket = self.__buckets[self._hash(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))

    def __delitem__(self, key: K) -> None:
        bucket = self.__buckets[self._hash(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return
        raise KeyError(key)

    def items(self) -> list[tuple[K, V]]:
        result = []
        for bucket in self.__buckets:
            result.extend(bucket)
        return result



class _MinHeap[T]:
    """
    A min heap implementation using a list.

    We store it as a list, but the data is accessed as a heap/tree. With the minimum value at the root.
    """
    def __init__(self) -> None:
        self.__data: list[T] = []

    def __len__(self) -> int:
        return len(self.__data)

    def peek(self) -> T:
        if not self.__data:
            raise IndexError("heap is empty")
        return self.__data[0]

    def push(self, item: T) -> None:
        self.__data.append(item)
        self._bubble_up(len(self.__data) - 1)

    def pop(self) -> T:
        if not self.__data:
            raise IndexError("heap is empty")
        self.__data[0], self.__data[-1] = self.__data[-1], self.__data[0]
        item = self.__data.pop()
        if self.__data:
            self._bubble_down(0)
        return item

    def _bubble_up(self, i: int) -> None:
        """
        Here we find the 'parent' index compare to the current item. Then swap if the parent is larger.
        Then bubble up the swapped item until it is in the correct position.

        :param i: The index of the item to bubble up
        :return:
        """
        parent = (i - 1) // 2
        if i > 0 and self.__data[i] < self.__data[parent]:
            self.__data[i], self.__data[parent] = self.__data[parent], self.__data[i]
            # we recursively call here, but as we are a heap even on very large trees (10000 items), we should have about 13 levels.
            self._bubble_up(parent)

    def _bubble_down(self, i: int) -> None:
        """
        Find the smallest child and swap with the current item if the child is smaller.
        Then bubble down the swapped item until it is in the correct position.

        :param i: The index of the item to bubble down
        :return:
        """
        smallest, left, right = i, 2 * i + 1, 2 * i + 2
        if left < len(self.__data) and self.__data[left] < self.__data[smallest]:
            smallest = left
        if right < len(self.__data) and self.__data[right] < self.__data[smallest]:
            smallest = right
        if smallest != i:
            self.__data[i], self.__data[smallest] = self.__data[smallest], self.__data[i]
            # we recursively call here, but as we are a heap even on very large trees (10000 items), we should have about 13 levels.
            self._bubble_down(smallest)

    def items(self) -> list[tuple[str, int]]:
        """
        Retrieve all counts as a list of tuples.

        :return: A list of tuples containing the value and its count
        """
        result = []
        while len(self.__data) > 0:
            count, word = self.__data.pop()
            result.append((word, count))
        result.reverse()
        return sorted(result, key=lambda x: x[1], reverse=True)

class CounterDict:
    """
    CounterDict allows us to count the frequency of words and retrieve the top k most frequent words.
    """
    def __init__(self):
        self.counts = _Dict[str,int](8192)

    def count(self, word: str) -> None:
        """
        Count a word. This will add or increase the count for the word.

        :param word: The word to count
        :return: None
        """
        if word is None:
            raise ValueError("Word cannot be None")
        try:
            self.counts[word] += 1
        except KeyError:
            self.counts[word] = 1

    def top_k(self, k: int) -> list[tuple[str, int]]:
        """
        Retrieve the top k most frequent words.

        :param k: The number of top words to retrieve
        :return: A list of tuples containing the word and its count, sorted by count in descending order
        """
        if k <= 0:
            raise ValueError("k must be positive")
        # we use a custom min heap to efficiently retrieve the top k elements
        heap: _MinHeap[tuple[int, str]] = _MinHeap()
        for word, count in self.counts.items():
            if len(heap) < k:
                # while we are under the limit, add the word to the heap
                heap.push((count, word))
            elif count > heap.peek()[0]:
                # now only push if the count is higher than the smallest count in the heap
                heap.pop()
                heap.push((count, word))

        return heap.items()

