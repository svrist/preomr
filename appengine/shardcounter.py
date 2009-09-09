#from http://code.google.com/appengine/articles/sharding_counters.html
from google.appengine.api import memcache
from google.appengine.ext import db
import random

class GeneralCounterShardConfig(db.Model):
  """Tracks the number of shards for each named counter."""
  name = db.StringProperty(required=True)
  num_shards = db.IntegerProperty(required=True, default=20)


class GeneralCounterShard(db.Model):
  """Shards for each named counter"""
  name = db.StringProperty(required=True)
  count = db.IntegerProperty(required=True, default=0)
 
           
def get_count(name):
  """Retrieve the value for a given sharded counter.
 
  Parameters:
    name - The name of the counter 
  """
  total = memcache.get(name)
  if total is None:
    total = 0
    for counter in GeneralCounterShard.all().filter('name = ', name):
      total += counter.count
    memcache.add(name, str(total), 60)
  return total

 
def increment(name):
  """Increment the value for a given sharded counter.
 
  Parameters:
    name - The name of the counter 
  """
  config = GeneralCounterShardConfig.get_or_insert(name, name=name)
  def txn():
    index = random.randint(0, config.num_shards - 1)
    shard_name = name + str(index)
    counter = GeneralCounterShard.get_by_key_name(shard_name)
    if counter is None:
      counter = GeneralCounterShard(key_name=shard_name, name=name)
    counter.count += 1
    counter.put()
  db.run_in_transaction(txn)
  memcache.incr(name)

 
def increase_shards(name, num): 
  """Increase the number of shards for a given sharded counter.
  Will never decrease the number of shards.
 
  Parameters:
    name - The name of the counter
    num - How many shards to use
   
  """
  config = GeneralCounterShardConfig.get_or_insert(name, name=name)
  def txn():
    if config.num_shards < num:
      config.num_shards = num
      config.put()   
  db.run_in_transaction(txn)
