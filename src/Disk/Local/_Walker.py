from _Paths import FolderPath
from ..Walker import WalkerAbstract
import os

class LocalFolderWalker(WalkerAbstract):
	"""Implementation of WalkerAbstract for folders on the local system."""
	def __init__(self):
		super(LocalFolderWalker, self).__init__()
	@classmethod
	def _getOSwalkResults(cls, folder, topDown, followSymlinks):
		return os.walk(str(folder), topdown=topDown, followlinks=followSymlinks)

WalkerAbstract._registerType(LocalFolderWalker, FolderPath)
