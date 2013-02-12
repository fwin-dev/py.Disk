from Disk.Walker import WalkerAbstract
from _Paths import FolderPath
from Net import SSH

class SSHFolderWalker(WalkerAbstract):
	def __init__(self):
		super(SSHFolderWalker, self).__init__(FolderPath)
	@classmethod
	def _getOSwalkResults(cls, folder, topDown, followSymlinks):
		cmd = "[i for i in os.walk(" + SSH.escapePath(folder) + ", topdown=" + str(topDown) + ", followlinks=" + str(followSymlinks) + ")]"
		return folder.connection.runPyCode_singleFunction(cmd, "os")

WalkerAbstract._registerType(SSHFolderWalker, FolderPath)
