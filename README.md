# voyager-numpy2-1d-query-repro

Repro for https://github.com/spotify/voyager/issues/117 (I'm not the reporter, just tried to reproduce it).

With voyager 2.0.6 or earlier and numpy 2.x, querying with a single 1-D vector returns the first neighbor k times.
No error, no warning. Passing the same vector as a 2-D array works. **It does not reproduce on 2.0.7 or later,
including 2.2.3.**

This is the same bug as https://github.com/spotify/voyager/issues/68, which was fixed in 2.0.7 by
https://github.com/spotify/voyager/pull/69. That PR also added a regression test and started running the tests
against the built wheels in CI.

The issue doesn't say which voyager version was installed in the numpy 2.2.3 environment. This repro assumes it was
still 2.0.6. The reported output matches that: a flat array of length k (what 1-D queries return), with the correct
first id and distance repeated.

## Steps

`repro.py` does create → save → load → query:

```sh
# 1. create and save with voyager 2.0.6 + numpy 1.26.4
uv run --no-project --python 3.12 --with voyager==2.0.6 --with numpy==1.26.4 python repro.py save index.voy

# 2. load and query with voyager 2.0.6 + numpy 2.2.3
uv run --no-project --python 3.12 --with voyager==2.0.6 --with numpy==2.2.3 python repro.py query index.voy
```

```
voyager 2.0.6, numpy 2.2.3, python 3.12.12
1-D query ids:       [0 0 0 0 0]
1-D query distances: [0. 0. 0. 0. 0.]
2-D query ids:       [  0 300 631 546 581]
BUG: 1-D query does not match 2-D query
```

`./run_all.sh` saves once and then loads/queries with each pair in the table. It always exits 0; read the output.

You need [uv](https://docs.astral.sh/uv/). Python is pinned to 3.12 because voyager 2.0.6/2.0.7 only ship wheels up to
cp312 (no sdist), and numpy 2.2.x needs 3.10+. On Windows, run the commands above directly with other versions
swapped in. With Docker:

```sh
docker build -t voyager-117-repro .
docker run --rm voyager-117-repro
```

## Results

Index saved with voyager 2.0.6 + numpy 1.26.4, then loaded and queried with:

| voyager | numpy | 1-D query | 2-D query |
| --- | --- | --- | --- |
| 2.0.6 | 1.26.4 | ok | ok |
| 2.0.5 | 2.2.3 | repeats first id | ok |
| 2.0.6 | 2.2.3 | repeats first id | ok |
| 2.0.6 | 2.2.6 | repeats first id | ok |
| 2.0.7 | 2.2.6 | ok | ok |
| 2.2.3 | 2.2.3 | ok | ok |
| 2.2.4 | 2.2.6 | ok | ok |

Same results on macOS arm64 (Python 3.12) and in Docker on linux/arm64 and linux/amd64 (amd64 emulated). I haven't
tried Windows or Intel macOS.

Also checked by hand, not in this repo:

- 2.0.2 with numpy 2.2.3 breaks the same way.
- 2.0.6 also breaks on Python 3.9, 3.10 and 3.11 with numpy 2.x.
- Euclidean, Cosine and InnerProduct all break. So do float64 and plain list queries.
- 2.0.8 through 2.2.2 with numpy 2.2.6 are fine.

## Notes

- Save/load isn't needed to hit it. A fresh in-memory index on 2.0.6 + numpy 2 does the same thing. Only the voyager
  version on the query side matters.
- `python/bindings.cpp` is the same in v2.0.6 and v2.0.7. The only C++ change between them is an unrelated atomic
  label counter in `cpp/TypedIndex.h` (#70). So my guess is the pybind11 version the wheels were built with. It isn't
  pinned (`pybind11>=2.0`), 2.0.6 was tagged on 2024-03-22, and pybind11 2.12.0, the first release that supports
  numpy 2, came out on 2024-03-27. Not verified.
- Workaround: upgrade to 2.0.7+, or query with `vector[None, :]` and take `ids[0]`, `distances[0]`.
