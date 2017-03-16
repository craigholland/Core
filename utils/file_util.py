import os, sys

from utils import constants

class File(object):
  """Basic File Object class."""

  def __init__(self, path, filename):
    self.path_exists = False
    self.file_exists = False
    self.path = constants.ROOT_PATH + '/' + path
    self.file = filename
    self._permissions = {
      'append': False,
      'create': False,
      'replace': False,
      'createDir': False
    }
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
      if self._append and self._permissions['append']:
        return open(path, 'ab')
      elif self._replace and self._permissions['replace']:
        return open(path, 'w+b')
      else:
        return open(path, 'rb')
    elif self._create and self._permissions['create']:
      return open(path, 'w+b')

  def enableAllPermissions(self, set_value=True):
    for k, v in self._permissions:
      self._permissions[k] = set_value

  @property
  def toggleAppend(self):
    self._permissions['append'] = not self._permissions['append']
    return self._permissions['append']

  @property
  def toggleCreate(self):
   self._permissions['create'] = not self._permissions['create']
   return self._permissions['create']

  @property
  def toggleReplace(self):
   self._permissions['replace'] = not self._permissions['replace']
   return self._permissions['replace']

  @property
  def toggleCreateDir(self):
    self._permissions['createDir'] = not self._permissions['createDir']
    return self._permissions['createDir']

  def createPath(self):
    """If specified path doesn't exist, this creates it."""
    path = constants.ROOT_PATH
    if self._permissions['createDir']:
      for folder in self.path.replace(path + '/', '').split('/'):
        path += '/{0}'.format(folder)
        if not os.path.isdir(path):
          os.mkdir(path)
      if os.path.isdir(path):
        self.path_exists = True
      return True
    return False


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
    if self.file_exists and self._permissions['append']:
      self._append = True
      with self._file_object as f:
        f.write(txt)
      self._append = False

    elif self._permissions['create']:
      self._create = True
      with self._file_object as f:
        f.write(txt)
      self.file_exists = True
      self._create = False




