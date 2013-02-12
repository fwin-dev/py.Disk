from _Paths import FilePath, FolderPath
from _File import File
import _Walker	# forces registration

from .. import _base
_base.PathAbstract._registerType(File, FilePath, FolderPath)
