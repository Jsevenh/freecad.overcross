"""Entry point of the RobotCAD workbench."""
import os
import sys
import FreeCAD as fc
from .ros.utils import add_ros_library_path
from .version import __version__
from .wb_globals import g_ros_distro
from .freecad_utils import pip_install
    

try:
    # For v0.21:
    from addonmanager_utilities import get_python_exe
except (ModuleNotFoundError, ImportError):
    # For v0.22/v1.0:
    from freecad.utils import get_python_exe


# Initialize debug with debugpy.
if os.environ.get('DEBUG'):
    print('DEBUG attaching...')
    # how to use:
    # DEBUG=1 command_to_run_freecad
    # Use Ubuntu or install manually debugpy module FreeCAD python and FreeCAD python version to OS.
    # turn on Debugger in VSCODE and add breakpoints to code
    # Cf. https://github.com/FreeCAD/FreeCAD-macros/wiki/Debugging-macros-in-Visual-Studio-Code.

    def attach_debugger():
        import debugpy
        debugpy.configure(python=get_python_exe())
        debugpy.listen(("0.0.0.0", 5678))
        # debugpy.wait_for_client()
        debugpy.trace_this_thread(True)
        debugpy.debug_this_thread()
        print('DEBUG attached.')

    try:
        attach_debugger()
    except:
        pip_install('debugpy', restart_freecad = False)
        attach_debugger()

        
add_ros_library_path(g_ros_distro)

# Must be imported after the call to `add_ros_library_path`.
from .ros.utils import is_ros_found  # noqa: E402.

if is_ros_found():
    fc.addImportType('URDF files (*.urdf *.xacro)', 'freecad.cross.import_urdf')

try:
    import urdf_parser_py
except (ModuleNotFoundError, ImportError):
    pip_install('urdf_parser_py', restart_freecad = False)

try:
    import xacro
except (ModuleNotFoundError, ImportError):
    pip_install('xacro', restart_freecad = False)

try:
    import xmltodict
except (ModuleNotFoundError, ImportError):
    pip_install('xmltodict', restart_freecad = False)
