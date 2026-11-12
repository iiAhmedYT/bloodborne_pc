# Sourced by the Windows build/run scripts: puts the MSYS2 CLANG64 toolchain first on PATH.
# In an MSYS2 shell '/' is the installation root (C:/msys64 for a normal MSYS2 install, a
# temporary directory such as D:/a/_temp/msys64 for msys2/setup-msys2 on hosted runners), so
# it is discovered rather than assumed. MSYS2_ROOT overrides it, as a path in either notation.
msys2_root=${MSYS2_ROOT:-/}
msys2_root=${msys2_root%/}
if [[ $msys2_root =~ ^([A-Za-z]):[\\/](.*)$ ]]; then
    msys2_root="/${BASH_REMATCH[1],,}/${BASH_REMATCH[2]//\\//}"
fi
if [[ -d $msys2_root/clang64/bin ]]; then
    export PATH="$msys2_root/clang64/bin:$msys2_root/usr/bin:$PATH"
    export MSYSTEM=CLANG64
fi
