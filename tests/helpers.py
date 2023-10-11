import re
import sys
import textwrap
from os.path import basename, dirname, realpath
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader


def import_path(path: str):
    module_name = basename(path).replace("-", "_")
    spec = spec_from_loader(module_name, SourceFileLoader(module_name, path))
    assert spec
    assert spec.loader
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def dedent(text: str) -> str:
    return textwrap.dedent(re.sub(r"^\n", "", text, re.S))


git_grok = import_path(dirname(dirname(realpath(__file__))) + "/git-grok")
