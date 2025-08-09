{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.flake-utils.inputs.systems.follows = "systems";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  inputs.systems.url = "github:nix-systems/default";

  outputs =
    {
      self,
      flake-utils,
      nixpkgs,
      ...
    }@inputs:
    let
      inherit (nixpkgs) lib;
    in
    {
      pythonPackageExtensions = {
        ml4dqmdc-pixelae = (
          final: previous: {
            ml4dqmdc-pixelae = final.callPackage ./ml4dqmdc-pixelae-package.nix { };
          }
        );
      };
    }
    // flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python3-ml4dqmdc-pixelae = pkgs.python3.override {
          packageOverrides = self.pythonPackageExtensions.ml4dqmdc-pixelae;
        };
      in
      {
        checks = {
          ml4dqmdc-pixelae-python3 = python3-ml4dqmdc-pixelae.pkgs.ml4dqmdc-pixelae;
        };
        devShells = {
          default = self.devShells.${system}.ml4dqmdc-pixelae;
          ml4dqmdc-pixelae = pkgs.mkShell {
            pname = "ml4dqmdc-pixelae-development-shell";
            inherit (python3-ml4dqmdc-pixelae.pkgs.ml4dqmdc-pixelae) version;
            packages =
              (with pkgs.python3Packages; [
                notebook
              ])
              ++ lib.concatLists (
                lib.attrValues self.checks.${system}.ml4dqmdc-pixelae-python3.optional-dependencies
              );
            inputsFrom = [
              self.checks.${system}.ml4dqmdc-pixelae-python3
            ];
          };
        };
      }
    );
}
