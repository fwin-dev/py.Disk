from Local import FolderPath

import random, string

class TempFolderPath(FolderPath):
	"""
	Creates a random directory path for temporary use. Note that this class will not actually create the folder.
	
	Folders have a 'py_' prefix so they are easy to spot in the terminal.
	"""
	def __init__(self):
		LENGTH = 6
		dir_ = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(LENGTH))
		dir_ = "/tmp/py_" + dir_
		FolderPath.__init__(self, dir_)
