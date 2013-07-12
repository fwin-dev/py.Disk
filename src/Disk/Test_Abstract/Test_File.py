from abc import ABCMeta, abstractproperty

class FileAbstract:
	__metaclass__ = ABCMeta
	
	@abstractproperty
	def filePath(self):
		"""Path to a non-existing file for testing. Parent folder must already exist."""
		pass
	
	def setUp(self):
		super(FileAbstract, self).setUp()
		assert not self.filePath.exists()
		assert self.filePath.dirname().exists()
	def tearDown(self):
		super(FileAbstract, self).tearDown()
		if self.filePath.exists():
			self.filePath.remove()
		assert not self.filePath.exists()
	
	def test_writeNonExistFile_empty(self):
		file_ = self.filePath.asFile("w+b")
		with file_:
			contents = file_.read()
		self.assertTrue(self.filePath.exists())
		self.assert_(len(contents) == 0, "len(empty file) == 0")
	
	def test_writeNonExistFile(self):
		file_ = self.filePath.asFile("w+b")
		with file_:
			file_.write("foo")
		self.assertTrue(self.filePath.exists())
		self.assert_(file_.getPath().stat().st_size > 0, "len(written file) == 0")
	
	def test_repr(self):
		file_ = self.filePath.asFile("w+b")
		str(file_)
	
	def test_noWith_misc(self):
		with self.filePath.asFile("w+b") as file_:
			self.assertTrue(file_.isWritable())
			self.assertTrue(not file_.isClosed())
			file_.write("asdf")
		self.assertTrue(not file_.isWritable())
		self.assertTrue(file_.isClosed())
		
		file_.reopen("r")	# reopen with mode change
		contents1 = file_.read()
		file_.close()
		file_.close()	# test double close() call - should not raise an exception
		
		with self.assertRaises(AttributeError):
			file_.read()	# test premature read when file isn't open
		
		file_.reopen()
		contents2 = file_.read()
		self.assertTrue(contents1 == contents2)
		
		with self.assertRaises(AttributeError):
			file_.asdf		# since attribute lookup is modified, test for invalid attribute access while file is open
		file_.destruct()
		self.assertTrue(file_.isClosed())
		

# 	def test_utime(self):
# 		"""File timestamp precisions can differ across filesystems and between python versions"""
# 		filePath1 = self.folder.joinFile("utime1.txt")
# 		filePath2 = self.folder.joinFile("utime2.txt")
# 		filePath1.create()
# 		filePath2.create()
# 		filePath2.utime(filePath1.getatime()-1000, filePath1.getmtime()-1000)
