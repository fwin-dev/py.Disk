from Disk.Test_Abstract import Test_Walker
from Disk.TempFolder import TempFolderPath
from Disk.TempFile import NamedSecureTempFile

import unittest

class Test_TempFolder(unittest.TestCase):
	def test_creation(self):
		TempFolderPath()

class Test_NamedSecureTempFile(unittest.TestCase):
	def test_deletion(self):
		with NamedSecureTempFile(delete=True) as file_:
			file_.write("asdf")
		self.assertTrue(file_.getPath().exists())
		file_.destruct()
		self.assertTrue(not file_.getPath().exists())
