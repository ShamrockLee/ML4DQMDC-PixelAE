import pathlib
import sys

_file_path = pathlib.Path(__file__)

if not _file_path.is_symlink():
    print("_import_adapter.py is meant to be the symlinked target from a legacy Python module location", file=sys.stderr)
    exit(1)

_target_class_name = _file_path.stem

_root_module_string = "ml4dqmdc"
_root_module_path = ""
_submodule_string = ""
_file_path_parent_name = _file_path.parent.name
if _file_path_parent_name == "src":
    _root_module_path = _file_path.parent / _root_module_string
if _file_path_parent_name in ("classifiers", "cloudfitters"):
    _submodule_string = _file_path_parent_name
    _root_module_path = _file_path.parent.parent / _root_module_string
if _file_path_parent_name == "utils":
    _submodule_string = "{}.{}".format(_file_path_parent_name, _target_class_name)
    _root_module_path = _file_path.parent.parent / "src" / _root_module_string
    _target_class_name = ""

_target_module_string = _root_module_string if _submodule_string == "" else "{}.{}".format(_root_module_string, _submodule_string)

print("{} import adapter: from {} import {}".format(_root_module_string, _target_module_string, "*" if not _target_class_name else _target_class_name), file=sys.stderr)

del _file_path_parent_name
del _file_path

_target_module = None

try:
    _target_module = __import__(_target_module_string, fromlist=[_target_class_name])
except ImportError:
    if _target_module_string in dir(sys.modules):
        print("reusing {} {}".format(_target_module_string, _target_module), file=sys.stderr)
        _target_module = sys.modules[_target_module_string]
    else:
        _root_module = None
        if _root_module_string in dir(sys.modules):
            print("reusing {} {}".format(_root_module_string, _root_module), file=sys.stderr)
            _root_module = sys.modules[_root_module_string]
        else:
            print("loading from {}".format(_root_module_path), file=sys.stderr)
            import importlib.util
            _root_module_spec = importlib.util.spec_from_file_location(_root_module_string, _root_module_path / "__init__.py")
            _root_module = importlib.util.module_from_spec(_root_module_spec)
            sys.modules[_root_module_string] = _root_module
            _root_module_spec.loader.exec_module(_root_module)
            del _root_module_spec
        import operator
        _target_module = operator.attrgetter(_submodule_string)(_root_module)
        sys.modules[_target_module_string] = _target_module
        del _root_module

del _root_module_path
del _root_module_string
del _submodule_string
del _target_module_string

if _target_class_name == "":
    # https://stackoverflow.com/questions/41990900/what-is-the-function-form-of-star-import-in-python-3/41991139#41991139
    _target_module_member_names = getattr(_target_module, "__all__",
        [name for name in dir(_target_module) if not name.startswith("_")])
    globals().update({name: getattr(_target_module, name) for name in _target_module_member_names})
    del _target_module_member_names
else:   
    globals()[_target_class_name] = getattr(_target_module, _target_class_name)

del _target_class_name
del _target_module
print(file=sys.stderr)
