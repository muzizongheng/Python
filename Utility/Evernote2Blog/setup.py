import sys 


if ".\\evernote-sdk-python3-master\\lib" not in sys.path:
    sys.path.append(".\\evernote-sdk-python3-master\\lib")

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors


from cx_Freeze import setup, Executable

## Dependencies are automatically detected, but it might need
## fine tuning.
buildOptions = dict(packages = [], excludes = [], include_files={"config", "Readme.md", "pingcfg", "existedBlog"})

executable = "Main.py"
base = "Console"
targetName = "evernote2Blog.exe"

executables = [Executable(executable, base=base, targetName=targetName)]


setup(name="evernote2Blog", version ="1.0", description ="convert evernote notes to blog.",options = dict(build_exe = buildOptions),
      executables = executables)

# import sys
# from cx_Freeze import setup, Executable

# # Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# # GUI applications require a different base on Windows (the default is for a
# # console application).
# base = "Console"

# setup(  name = "guifoo",
        # version = "0.1",
        # description = "My GUI application!",
        # options = {"build_exe": build_exe_options},
        # executables = [Executable("Main.py", base=base)])