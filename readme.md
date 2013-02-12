Package description	{#mainpage}
===================

# Summary of functionality

The Disk API is fairly big and provides:

- Abstracted Path objects for files and folders
- Abstracted File object
- Temporary files and folders
- A better walk() function for getting files/subfolders inside a folder
- Remote disk objects that work over SSH
- __One unified API for all of the above__
- An improved ZipFile class
- A configuration file parser for modifying config files with key+value pairs

# Detailed functionality

## Representing file and folder paths

	from Disk import Local
	filePath = Local.FilePath("path/to/file.txt")
	folderPath = Local.FolderPath("path/to/local/folder")

`FilePath` instances have methods similar to what is available in python's built in `os.path`, except that the
first argument of all methods in `os.path` is not needed because functions in `os.path` are not attached to a
class instance, whereas functions belonging to a `FilePath` class are. (This is similar to the move from all
string functions being stored in the `string` module to becoming methods of string objects.) For example, to
get the `dirname` of a path, do:

	folderPath = filePath.dirname()

`folderPath` will be an instance of `Disk.Local.FolderPath`.

90% of functions available in `os.path` are identically implemented as object methods in FilePath and FolderPath.
In addition, some additional functions (many from `shutil`) are also available:

- For `FilePath` objects:
  - `move(destinationFilePath)`
  - `rename(newFilename)`
  - `copy(destinationFilePath, shouldCopyDates)`
  - `create()` - Similar to `touch`
- For `FolderPath` objects:
  - `remove(isRecursive)`
  - `mkdirs()`/`makedirs()` - Same as `os.path.makedirs`
  - `walk(...)` - See below

### Walking a folder

Python has 2 stock implementations of a folder walker, each with its own features. A 3rd implementation is
introduced here, with even more features:

	subItems = folderPath.walk(isRecursive, wantFiles, wantFolders, followSymlinks=False, nameGlob="*", topDown=True)

`subItems` will be a `list` of `FilePath`s and/or `FolderPath`s, depending on `wantFiles` and `wantFolders`.

### Temporary folders

Temporary folders are the same as a `Local.FolderPath` above, with a pre-set folder name and path:

	from Disk.TempFolder import TempFolderPath
	folder = TempFolderPath()

## File objects

File objects here are similar to the objects returned by python's built in `open()` function, but have some
differences/improvements. Here are some examples:

	from Disk import Local
	file_ = Local.File("/path/to/file", "r")
	
	if file_.isWritable():
		# determines if the file can be written to using the mode specified
	if file_.isClosed():
		# do something
	print(file_.getPath())
	
	with file_:
		# use standard read/write methods here
	with file_:
		# files can be reopened later, after being closed by the `with` statement above

### Temporary files

Temporary files are the same as a `Local.File` above, except they have the option to be deleted when they are destructed.
`NamedSecureTempFile` is basically a combination of python's built-in `tempfile.NamedTemporaryFile` and `tempfile.mkstemp`.

	from Disk.TempFile import NamedSecureTempFile as TempFile
	file_ = TempFile(delete=True)
	with file_:
		# do something
	file_.destruct()	# permanently closes the file, and possibly deletes it

## Remote files and folders using SSH

There are identical `FilePath`, `FolderPath`, and `File` classes as mentioned above, but for SSH! Use them the same way.
Also, these 3 classes can be mixed interchangably in arguments, so for example, a `Local.FilePath` can be copied to a
`SSH.FilePath` using the same API:

	from Disk import Local, SSH
	source = Local.FilePath("path/to/file.txt")
	dest = SSH.FilePath("remote/path/to/file.txt")
	source.copy(dest)

## Improved ZipFile

The built in python `ZipFile` module/class has a bug where unix chmod file attributes within the zip are not restored
when unzipped. The new `ZipFile` module included here fixes that.

	from Disk.CompressedFile import ZipFile
	zipFile = ZipFile("path/to/myZippedFile.zip")
	zipFile.extract(folder)

## Configuration file modifier

This class has been designed to modify configuration files which have a list of key+value pairs in a certain format.
This format includes most configuration files.

	from Disk.ConfigFile import Parser_m1 as ConfigFile
	ConfigFile.changeConfig(filePath, newLine, commentChar='#', assignChar=' ', sectionName=None, sectionMatch='[')

`commentChar` is the character or string that is placed at the beginning of a comment in the config file
`assignChar` is the character or string between the key and value. Sometimes this is an equals sign.
`sectionName` should be used only if the config file has sections, ex. `[mysqld]`.
`sectionMatch` is the beginning character/string before the `sectionName`. This is ignored if `sectionName` is `None`.

