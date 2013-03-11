from Disk.Local import FolderPath
srcFolder = FolderPath("~/Desktop/test_folder").expanduser()
destFolder = FolderPath("~/Desktop/test_folder_bak").expanduser()
srcFolder.copy(destFolder)
