from abc import ABCMeta, abstractmethod, abstractproperty

class Test_File_Abstract:
	__metaclass__ = ABCMeta
	
	srcFilePath = None
	"""Must not already exist. This file path will be used to copy data from, in order to test `destFilePath`."""
	destFilePath = None
	"""Must not already exist. This will be the primary class (`Disk.AbstractFilePath` instance) to be tested."""
	
	def setUp(self):
		self._writeSrcFile()
		assert not self.destFilePath.exists()
	def _writeSrcFile(self):
		assert not self.srcFilePath.exists()
		with self.srcFilePath.asFile("w") as srcFile:
			srcFile.write("abcdef\nghijkl\n")
		assert self.srcFilePath.getsize() > 0
	def tearDown(self):
		if self.destFilePath.exists():
			self.destFilePath.remove()
		if self.srcFilePath.exists():
			self.srcFilePath.remove()
	
	def test_copy_withModifiedDate(self):
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		self.srcFilePath.copy(self.destFilePath, shouldCopyDates=True)
		self.assertTrue(self.srcFilePath.exists() and self.srcFilePath.getsize() > 0, "Source file was modified on a copy operation!!")
		self.assertEqual(self.srcFilePath.getsize(), self.destFilePath.getsize(), "Source file contents were not entirely copied to the destination file")
		
		# python 3.3 adds support for nanosecond precision, but < 3.3 only guarantees second precision
		self.assertEqual(int(self.srcFilePath.getmtime()), int(self.destFilePath.getmtime()), "Source file 'last modified' timestamp was not copied correctly to the destination file")
		
		self.destFilePath.remove()
		self.assertTrue(not self.destFilePath.exists(), "Failed to remove destination file")
	
	def test_move(self):
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		self.srcFilePath.move(self.destFilePath)
		self.assertTrue(not self.srcFilePath.exists(), "Failed to remove source file")
		self.assertTrue(self.destFilePath.getsize() > 0, "Destination file contents were not entirely moved from the source file")
		
		self.destFilePath.remove()
		self.assertTrue(not self.destFilePath.exists(), "Failed to remove destination file")

if __name__ == "__main__":
	unittest.main()
