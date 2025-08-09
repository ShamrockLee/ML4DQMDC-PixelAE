{
  lib,
  buildPythonPackage,
  setuptools,
  imageio,
  keras,
  matplotlib,
  numpy,
  pandas,
  requests,
  scikit-learn,
  six,
}:
let
  pyproject-metadata = lib.importTOML ./pyproject.toml;
in
buildPythonPackage {
  pname = pyproject-metadata.project.name;
  version = pyproject-metadata.project.version;
  pyproject = true;

  src = lib.fileset.toSource {
    root = ./.;
    fileset = lib.fileset.gitTracked ./.;
  };

  build-system = [
    setuptools
  ];

  dependencies = [
    keras
    matplotlib
    numpy
    pandas
    requests
    scikit-learn
    six
  ];

  optional-dependencies = {
    gif = [ imageio ];
  };

  doCheck = false;

  pythonImportsCheck = [
    "ml4dqmdc"
  ];

  meta = {
    description = pyproject-metadata.project.description;
  };
}
