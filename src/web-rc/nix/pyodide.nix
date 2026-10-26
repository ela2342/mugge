# Vendored Pyodide runtime for the standalone room correction (US-179).
#
# Pyodide 0.29.5 core plus the numpy and scipy wheels, laid out as one
# indexURL directory so loadPackage() finds the wheels next to
# pyodide-lock.json and nothing is fetched at runtime (AC1).
#
# Hashes: the core tarball digest is the one GitHub publishes for the
# release asset; the wheel hashes are the sha256 values in that tarball's
# own pyodide-lock.json.
{ lib, stdenvNoCC, fetchurl }:

let
  version = "0.29.5";
  cdn = "https://cdn.jsdelivr.net/pyodide/v${version}/full";

  core = fetchurl {
    url = "https://github.com/pyodide/pyodide/releases/download/${version}/pyodide-core-${version}.tar.bz2";
    sha256 = "ab08aafc11a3c9a0fe73825eb2cec78bda9464348dd17414e7ec0132ef3451e8";
  };

  wheels = [
    (fetchurl {
      url = "${cdn}/numpy-2.2.5-cp313-cp313-pyemscripten_2025_0_wasm32.whl";
      sha256 = "800c98edc0c864dfa49f07005680c699b4b42b84eae1f8cb19d35b3634e7f05c";
    })
    (fetchurl {
      url = "${cdn}/scipy-1.14.1-cp313-cp313-pyemscripten_2025_0_wasm32.whl";
      sha256 = "7a60ad5e52acd8d8059f4acc0932d701c3e07723d82e567523dd1a6e0e85ec3e";
    })
  ];

  # Only what the browser loads; the CLI launchers and .d.ts files stay out.
  coreFiles = [
    "pyodide.mjs"
    "pyodide.asm.js"
    "pyodide.asm.wasm"
    "python_stdlib.zip"
    "pyodide-lock.json"
  ];
in
stdenvNoCC.mkDerivation {
  pname = "web-rc-pyodide";
  inherit version;
  src = core;
  sourceRoot = "pyodide";

  dontConfigure = true;
  dontBuild = true;

  installPhase = ''
    runHook preInstall
    mkdir -p $out
    ${lib.concatMapStringsSep "\n" (f: "cp ${f} $out/") coreFiles}
    ${lib.concatMapStringsSep "\n" (w: "cp ${w} $out/${w.name}") wheels}
    runHook postInstall
  '';

  meta = {
    description = "Pyodide ${version} with numpy and scipy, for offline use";
    license = lib.licenses.mpl20;
    platforms = lib.platforms.all;
  };
}
