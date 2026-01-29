{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.flake-utils.inputs.systems.follows = "systems";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
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
        packages = {
          apptainer-image-python-for-jobs = pkgs.singularity-tools.buildImage {
            name = "apptainer-image-python-for-jobs";
            singularity = pkgs.apptainer;
            diskSize = 12288;
            memSize = 4096;
            contents = (with pkgs; [
              bash
              coreutils
              findutils
              # MiKTeX is a minimal LaTeX implementation (contrast to TeX Live).
              # It provide bin/latex for MatPlotLib to render text,
              # needed sometimes even when no text is specified.
              miktex
              parallel
            ])
            ++ [
              (python3-ml4dqmdc-pixelae.withPackages (ps: with ps;
                (lib.concatLists (
                  lib.attrValues ml4dqmdc-pixelae.optional-dependencies
                ))
                ++ ml4dqmdc-pixelae.dependencies
                ++ [ ml4dqmdc-pixelae ]
              ))
            ];
          };
        };
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
              )
              ++ (with pkgs; [
                # Interactive Bash with Readline support
                bash
              ]);
            inputsFrom = [
              self.checks.${system}.ml4dqmdc-pixelae-python3
            ];
          };
        };
      }
    );
}
