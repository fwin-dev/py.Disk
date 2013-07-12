from Disk.Test_Abstract import Test_Walker
import Disk.Local

import unittest

class LocalWalker(Test_Walker.WalkerAbstract, unittest.TestCase):
	folderPath = Disk.Local.FolderPath("/tmp/py_test_walker")
