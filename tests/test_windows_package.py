"""packaging/windows/package.sh and the Windows workflow: the ZIP must carry the CLANG64 runtime DLLs of
the executables in it, must not be written without them, and the release must carry the corresponding
source of the fsr4vk provider. The single successful CI run shipped bin\\ with no DLLs at all, because
ldd resolves MSYS2's own ELF programs but prints nothing for PE ones."""
from paths import ROOT
import unittest

PACKAGE = ROOT / 'packaging' / 'windows' / 'package.sh'
WORKFLOW = ROOT / '.github' / 'workflows' / 'windows-build.yml'


class RuntimeDllTests(unittest.TestCase):
    def script(self):
        return PACKAGE.read_text(encoding='utf-8')

    def test_the_imports_are_read_from_the_executables(self):
        script = self.script()
        self.assertIn('objdump -p "$binary" | sed -n', script)  # DLL Name: lines of the PE headers
        self.assertIn('stage_runtime_dlls "$dest/bin/"*.exe', script)
        self.assertNotIn('ldd "$dest/bin/"*.exe', script)  # what shipped an empty bin\

    def test_a_dll_brings_its_own_imports(self):
        self.assertIn('queue+=("$source")', self.script())

    def test_windows_and_drivers_dlls_are_left_to_the_system(self):
        script = self.script()
        self.assertIn('$name == vulkan-1.dll', script)  # the driver's loader, as every release so far
        self.assertIn('[[ -n $source ]] || continue', script)  # kernel32, d3d12, ... are not CLANG64's

    def test_no_zip_without_them(self):
        script = self.script()
        self.assertIn('for dll in libc++.dll libunwind.dll libwinpthread-1.dll SDL3.dll; do', script)
        self.assertIn('Missing CLANG64 runtime DLL in the package', script)
        guard = script.index('Missing CLANG64 runtime DLL in the package')
        self.assertLess(guard, script.index("shutil.make_archive('dist/bbport-windows'"))


class WorkflowTests(unittest.TestCase):
    def workflow(self):
        return WORKFLOW.read_text(encoding='utf-8')

    def test_packaging_runs_the_msys2_that_was_installed(self):
        workflow = self.workflow()
        self.assertIn('id: msys2', workflow)
        self.assertIn('steps.msys2.outputs.msys2-location', workflow)
        self.assertNotIn(r'C:\msys64\usr\bin\bash.exe', workflow)  # a guess; the runner installs elsewhere
        self.assertIn('out/windows-package.log', workflow)

    def test_the_corresponding_source_is_published(self):
        workflow = self.workflow()
        self.assertGreaterEqual(workflow.count('dist/fsr4vk-*-src.zip'), 1)  # the artifact
        self.assertIn('release/fsr4vk-*-src.zip', workflow)  # and the release


if __name__ == '__main__':
    unittest.main()
