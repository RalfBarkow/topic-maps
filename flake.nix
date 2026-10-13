{
  description = "Independent Common Lisp Topic Maps test foundation";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/50ab793786d9de88ee30ec4e4c24fb4236fc2674";
  outputs = { self, nixpkgs }: let
    systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
    eachSystem = nixpkgs.lib.genAttrs systems;
  in {
    devShells = eachSystem (system: let pkgs = import nixpkgs { inherit system; }; in {
      default = pkgs.mkShell { packages = [ pkgs.sbcl pkgs.python3 pkgs.git ]; };
    });
  };
}
