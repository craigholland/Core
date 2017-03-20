"""Methods and Classes providing functionality for Builder mechanism."""
import collections
from utils import constants
from utils import log_util

"""
Builder() is a utility that builds an "object-oriented" dictionary.  Rather than
 a central repository that
 contains all definitions, Builder allows for more section-specific definitions
 to be defined in their local branch.  Further, since the parent Builder object
 is actually instantiated at the root level, then child objects can reference
 other child objects from other branches.

e.g-
Life = Builder('General definition of biologic material')
Life.file = 'build_life.json' (auto-generated filename)

root/build_life.py:
PARENT =  "root"
DEFINITONS = {
    "Animal": "Definition of animals"
    "Plant" : "Definition of plants"
    "Fungi": "Defintion of fungi"
}

root/some_branch/build_life.py:
PARENT = "Animal"
DEFINITIONS = {
  "Fish": "Definition of Fish"
  "Bird": "Definition of Birds"
  "Mammal": "Definition of Mammals

root/some_other_branch/build_life.py:
PARENT = "Mammal"
DEFINITIONS = {
  "Horse" : "Definition of Horse"
  "Donkey" : "Definition of Donkey"

root/yet_another_branch/build_life.py:
PARENT = "Horse, Donkey"
DEFINITIONS = {
  "Mule" : "Definition of Mule"

root/from_any_branch/from_any_file.py
from root import Life
All_life = Life()
All_life.Plant = "Def of plants"
All_life.Keys = ['Animal','Plant','Fungi']
All_life.Animal.Keys = ['Fish', 'Bird', 'Mammal']

>> print All_life.Animal.Horse.Donkey == All_life.Animal.Mule.Donkey
True
>> All_life.FindKey('Birds')
'All_life.Animal.Birds'
>> All_life.FindKey('Human')
False
>> All_life.FindKey('Mule')
['All_life.Animal.Mammal.Horse.Mule', 'All_life.Animal.Mammal.Donkey.Mule']
>> All_life.Search(All_life.FindKey('Mule'))
"Definiton of Mule"


"""




class Builder(object):
  """Base class for Builder objects."""
  build_identifer = 'build_'
  root = constants.ROOT_PATH
  # def _Discover(self):
  #   pass

  def __init__(self):
    self._dict = collections.defaultdict(list)
    self.name = self.__class__.__name__
    # self.parent_loc = where am I being initialized?
    self.ignore_paths = []  # local paths/branches to ignore during Discovery.

  # def build(self):
  #   """Initiates object build."""
  #   pass



