from Test_Abstract import Test_File_Abstract

import Disk.Local, Disk.SSH
from Net import SSH

import unittest

sshConnection = SSH.Connection("192.168.205.30", username="py_ssh_unit_tests", password="!bonz@it")

class Test_LocalFile_to_LocalFile(Test_File_Abstract, unittest.TestCase):
	srcFilePath = Disk.Local.FilePath("/tmp/py0001.txt")
	destFilePath = Disk.Local.FilePath("/tmp/py0002.txt")

class Test_LocalFile_to_SSHfile(Test_File_Abstract, unittest.TestCase):
	srcFilePath = Disk.Local.FilePath("/tmp/py0001.txt")
	destFilePath = Disk.SSH.FilePath(sshConnection, "/tmp/py0002.txt")

class Test_SSHFile_to_Localfile(Test_File_Abstract, unittest.TestCase):
	srcFilePath = Disk.SSH.FilePath(sshConnection, "/tmp/py0001.txt")
	destFilePath = Disk.Local.FilePath("/tmp/py0002.txt")

class Test_SSHFile_to_SSHfile(Test_File_Abstract, unittest.TestCase):
	srcFilePath = Disk.SSH.FilePath(sshConnection, "/tmp/py0001.txt")
	destFilePath = Disk.SSH.FilePath(sshConnection, "/tmp/py0002.txt")
