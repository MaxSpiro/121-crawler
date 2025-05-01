import json
from simhash import Simhash, SimhashIndex

class PersistentSimhashIndex:
  def __init__(self, filepath='simhash_index.json', k=5):
    self._filepath = filepath
    self._k = k
    try:
      with open(self._filepath, 'r') as f:
        self._data = json.load(f)
    except:
      self._data = {}
    
    self._index = SimhashIndex([(url, Simhash(int(hash_val))) for url, hash_val in self._data.items()], k=self._k)

  def add_doc(self, url, tokens):
    simhash = Simhash(tokens)
    self._data[url] = simhash.value
    self._index.add(url, simhash)
    with open(self._filepath, "w") as f:
      json.dump(self._data, f)
  
  def get_matches(self, tokens):
    simhash = Simhash(tokens)
    return self._index.get_near_dups(simhash)
