from Disk.Test_Abstract import Test_File
import Disk.Local

import unittest

class TestLocal(Test_File.FileAbstract, unittest.TestCase):
	filePath = Disk.Local.FilePath("/tmp/py_test_file.txt")
