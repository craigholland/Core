import os, sys

from utils import constants

class File(object):
  """Basic File Object class."""

  def __init__(self, path, filename):
    self.path_exists = False
    self.file_exists = False
    self.path = constants.ROOT_PATH + '/' + path
    self.file = filename
    self._permit_append = False
    self._permit_create = False
    self._permit_replace = False
    self._append = False
    self._create = False
    self._replace = False
    if os.path.isdir(self.path):
      self.path_exists = True
      if os.path.exists(self.path + '/' + self.file):
        self.file_exists = True

  @property
  def _file_object(self):
    path = (self.path + '/' + self.file)
    if self.file_exists:
      if self._append and self._permit_append:
        return open(path, 'ab')
      elif self._replace and self._permit_replace:
        return open(path, 'w+b')
      else:
        return open(path, 'rb')
    elif self._create and self._permit_create:
      return open(path, 'w+b')

  @property
  def toggleAppend(self):
    self._permit_append = not self._permit_append
    return self._permit_append

  @property
  def toggleCreate(self):
    self._permit_create = not self._permit_create
    return self._permit_create

  @property
  def toggleReplace(self):
    self._permit_replace = not self._permit_replace
    return self._permit_replace

  def createPath(self):
    """If specified path doesn't exist, this creates it."""
    print self.path 

  def ReadInParts(self, size):
    """Read parts of file in bytes (for very big files)."""
    if self.file_exists:
      with self._file_object as f:
        while True:
          r = f.read(size)
          if not r:
            break
          yield r

  def Read(self):
    if self.file_exists:
      with self._file_object as f:
        return f.read()
    else:
        return None

  def Readline(self):
    if self.file_exists:
      with self._file_object as f:
        while True:
          r = f.readline()
          if not r:
            break
          else:
            yield r

  def Replace(self, txt, newline=True):
    if self.file_exists:
      self._replace = True
      txt = txt+'\n' if newline else txt
      with self._file_object as f:
        f.write(txt)
      self._replace = False

  def Append(self, txt, newline=True):
    """Serves as a 'Write' for new files, and 'Append' for existing files.
    Args:
      txt: str, text to be written/appended.
      newline: bool, add newline char (\n) at end of txt
    """
    txt = txt+'\n' if newline else txt
    if self.file_exists and self._permit_append:
      self._append = True
      with self._file_object as f:
        f.write(txt)
      self._append = False

    elif self._permit_create:
      self._create = True
      with self._file_object as f:
        f.write(txt)
      self.file_exists = True
      self._create = False




