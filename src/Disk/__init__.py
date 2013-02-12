import _base, Local, SSH

from Walker import walk

import os.path

def _join(*paths):
	for i in range(0, len(paths)):
		_type = str
		if isinstance(paths[i], _base.File):
			paths[i] = paths[i].getPath()
		if isinstance(paths[i], _base.PathAbstract):
			_type = paths[i]
			paths[i] = paths[i].asStr()
	
	return _type, os.path.join(*paths)

def joinFile(*paths):
	""" Joins path components to make a file """
	_type, result = _join(*paths)
	if _type == str:
		return result
	else:
		return _type._makeFilePath(result)

def joinFolder(*paths):
	""" Joins path components to make a file """
	_type, result = _join(*paths)
	if _type == str:
		return result
	else:
		return _type._makeFolderPath(result)
