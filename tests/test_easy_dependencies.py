import importlib.util,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import dependencies,easy
class DependencyTests(unittest.TestCase):
 def test_families(self):
  with patch.object(Path,'exists',return_value=False):
   for distro,like,expected in [('fedora','','fedora'),('linuxmint','ubuntu debian','debian'),('endeavouros','arch','arch'),('unknown','','')]:
    self.assertEqual(dependencies.family({'ID':distro,'ID_LIKE':like}) or '',expected)
 def test_immutable_fedora_not_host_dnf(self):
  with patch.object(Path,'exists',return_value=True):self.assertIsNone(dependencies.family({'ID':'fedora'}))
 def test_auto_nix(self):
  with patch.object(easy.shutil,'which',side_effect=lambda n:'/usr/bin/nix' if n=='nix' else None):self.assertEqual(easy.choose_backend('auto','install'),'nix')
 def test_auto_fedora_without_nix(self):
  with patch.object(easy.shutil,'which',return_value=None),patch.object(dependencies,'family',return_value='fedora'):self.assertEqual(easy.choose_backend('auto','install'),'native')
 def test_reuses_native_for_run(self):
  with patch.object(easy.shutil,'which',return_value='/usr/bin/tool'):self.assertEqual(easy.choose_backend('auto','run'),'native')
 def test_no_shell_or_forced_confirm(self):
  for kind in ('fedora','debian','arch'):
   for cmd in dependencies.commands(kind):
    self.assertEqual(cmd[0],'sudo');self.assertNotIn('-y',cmd);self.assertNotIn('--noconfirm',cmd)
 def test_unknown_no_packages(self):self.assertEqual(dependencies.commands(None),[])
 def test_arch_full_upgrade(self):self.assertEqual(dependencies.commands('arch')[0][:4],['sudo','pacman','-Syu','--needed'])
if __name__=='__main__':unittest.main()
