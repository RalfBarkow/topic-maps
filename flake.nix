{
  description = "Independent Common Lisp Topic Maps test foundation";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/50ab793786d9de88ee30ec4e4c24fb4236fc2674";
  outputs = { self, nixpkgs }: let
    systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
    eachSystem = nixpkgs.lib.genAttrs systems;
    cxmlEnvironment = system: let
      pkgs = import nixpkgs { inherit system; };
      visit = package: [ package ] ++ builtins.concatLists
        (map visit (package.lispLibs or [ ]));
      # Sources, not FASLs compiled by Nixpkgs' SBCL version. The caller can
      # use the existing SBCL 2.5.4 without changing this Nixpkgs pin.
      packages = pkgs.lib.unique (visit pkgs.sbclPackages.cxml);
    in {
      # This registry names pristine sources. prepare-cxml.py applies the
      # following versioned patches to a separate copy before qualification/use.
      patchProfile = "19d0b-1";
      localPatches = map (name: {
        package = name;
        file = "patches/${name}-19d0b.patch";
        sha256 = builtins.hashFile "sha256" (./patches + "/${name}-19d0b.patch");
      }) [ "closure-common" "cxml" ];
      sourceRegistry = "(:source-registry " +
        pkgs.lib.concatMapStringsSep " "
          (package: "(:tree \"${package.src}/\")") packages +
        " :ignore-inherited-configuration)";
      manifest = map (package: {
        name = package.pname;
        inherit (package) version;
        source = toString package.src;
        url = package.src.url;
        sha256 = package.src.outputHash;
      }) packages;
    };
  in {
    # Evaluating this source environment needs no DevShell/toolchain rebuild.
    lib.cxmlEnvironment = cxmlEnvironment;
    devShells = eachSystem (system: let pkgs = import nixpkgs { inherit system; }; in {
      default = pkgs.mkShell {
        packages = [ pkgs.sbcl pkgs.python3 pkgs.git ];
        CL_SOURCE_REGISTRY = (cxmlEnvironment system).sourceRegistry;
      };
    });
  };
}
