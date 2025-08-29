from typing import Dict, Callable, Any
from .web import search as web_search, get as web_get
from .python_exec import py_exec
from .fs import fs_read, fs_write
from .shell import sh_run

def registry(enable_shell: bool = False, enable_python: bool = True, enable_fs: bool = True) -> Dict[str, Callable[..., Any]]:
    tools = {
        "web.search": web_search,
        "web.get": web_get,
    }
    if enable_python:
        tools["py.exec"] = py_exec
    if enable_fs:
        tools["fs.read"] = fs_read
        tools["fs.write"] = fs_write
    if enable_shell:
        tools["sh.run"] = sh_run
    return tools
