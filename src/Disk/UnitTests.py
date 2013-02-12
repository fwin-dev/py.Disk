import SSH, Local
import Net.SSH
import os, shutil, stat
import unittest

class PermBits(unittest.TestCase):
	def setUp(self):
		path = "/tmp/pyTest"
		os.mkdir(path)
		os.chmod(path, 0o0770)
	
	def tearDown(self):
		shutil.rmtree("/tmp/pyTest")
	
	def getTestFolder(self, isLocal):
		if isLocal:
			return Local.FolderPath("/tmp/pyTest")
		else:
			raise Exception()
	
#	def test_permissionBits_folder(self):
#		""" Subfolders made in a parent folder should, by default, retain the chmod permissions of the parent """
#		subfolder = self.getTestFolder(isLocal=True).join(Local.FolderPath("permBitsFolder"))
#		parentPerms = subfolder.dirname().stat().st_mode
#		subfolder.mkdir()
#		subfolderPerms = subfolder.stat().st_mode
#		self.assert_(parentPerms == subfolderPerms, str(parentPerms) + " == " + str(subfolderPerms))
#	
#	def test_permissionBits_file(self):
#		""" When files are created they should, by default, retain the chmod permissions of the parent """
#		filePath = self.getTestFolder(isLocal=True).join(Local.FilePath("permBitsFile"))
#		parentPerms = stat.S_IMODE(filePath.dirname().stat().st_mode)
#		filePath.create()
#		filePerms = stat.S_IMODE(filePath.stat().st_mode)
#		self.assert_(parentPerms == filePerms, str(parentPerms) + " == " + str(filePerms))


class TestSSH(object):
	def setUp(self):
		self.con = Net.SSH.Connection(host="192.168.205.30")
		self.folder = SSH.FolderPath(self.con, "/tmp/pyTest")
		assert not self.folder.exists()
		self.folder.mkdir()
	def tearDown(self):
		self.folder.remove(isRecursive=True)

class TestLocal(object):
	def setUp(self):
		self.folder = Local.FolderPath("/tmp/pyTest")
		assert not self.folder.exists()
		self.folder.mkdir()
	def tearDown(self):
		self.folder.remove(isRecursive=True)


class TestOSfuncs(unittest.TestCase, TestLocal):
	def test_utime(self):
		filePath1 = self.folder.joinFile("utime1.txt")
		filePath2 = self.folder.joinFile("utime2.txt")
		filePath1.create()
		filePath2.create()
		filePath2.utime(filePath1.getatime()-1000, filePath1.getmtime()-1000)

class SSHfile(unittest.TestCase, TestSSH):
	def test_emptyFile(self):
		file_ = self.folder.joinFile("test.txt").asFile("w+b")
		with file_:
			contents = file_.read()
		self.assert_(len(contents) == 0, "len(empty file) == 0")
	def test_writeNonExistFile(self):
		file_ = self.folder.joinFile("test2.txt").asFile("w+b")
		with file_:
			file_.write("foo")
		print(file_.getPath().stat().st_size)
		self.assert_(file_.getPath().stat().st_size > 0, "file size > 0")


class Walker:
	def _createTempFiles(self, folder, prefix=""):
		folder.create()
		filesMade = []
		for i in range(0, 4):
			filePath = folder.joinFile(prefix + str(i) + ".txt")
			filePath.create()
			filesMade.append(filePath)
		return filesMade
	
	def test_walk_folder_noRecurse(self):
		folder = self.folder.joinFolder("walk_test")
		subfolder = folder.joinFolder("subfolder")
		parentFilesMade = self._createTempFiles(folder)
		self._createTempFiles(subfolder, "sub")
		results = [i for i in folder.walk(wantFiles=True, wantFolders=False, isRecursive=False)]
		self._assert(set(parentFilesMade) == set(results), str(parentFilesMade) + "\n" + str(results))
	
	def test_walk_folder_recurse(self):
		folder = self.folder.joinFolder("walk_test")
		subfolder = folder.joinFolder("subfolder")
		filesMade = self._createTempFiles(folder)
		filesMade += self._createTempFiles(subfolder, "sub")
		results = [i for i in folder.walk(wantFiles=True, wantFolders=False, isRecursive=True)]
		self._assert(set(filesMade) == set(results), str(filesMade) + "\n" + str(results))

class SSHwalker(TestSSH, unittest.TestCase, Walker):
	pass
class LocalWalker(TestLocal, unittest.TestCase, Walker):
	pass


