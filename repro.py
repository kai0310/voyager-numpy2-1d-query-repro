# https://github.com/spotify/voyager/issues/117
#
#   python repro.py save index.voy    create an index and save it
#   python repro.py query index.voy   load it and query one vector as 1-D and as 2-D

import sys
from importlib.metadata import version

import numpy as np
import voyager

cmd, path = sys.argv[1], sys.argv[2]
data = np.random.default_rng(0).standard_normal((1000, 32)).astype(np.float32)
print(
    f"voyager {version('voyager')}, numpy {np.__version__}, python {sys.version.split()[0]}"
)

if cmd == "save":
    index = voyager.Index(voyager.Space.Cosine, num_dimensions=32)
    index.add_items(data)
    index.save(path)
    print(f"saved {path}")
    sys.exit(0)

index = voyager.Index.load(path)
ids_1d, distances_1d = index.query(data[0], k=5)
ids_2d, distances_2d = index.query(data[None, 0], k=5)

print("1-D query ids:      ", ids_1d)
print("1-D query distances:", distances_1d)
print("2-D query ids:      ", ids_2d[0])

if np.array_equal(ids_1d, ids_2d[0]):
    print("OK")
else:
    print("BUG: 1-D query does not match 2-D query")
    sys.exit(1)
