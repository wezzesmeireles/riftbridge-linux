import importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('riftgui',Path(__file__).resolve().parents[1]/'scripts/gui.py');gui=importlib.util.module_from_spec(spec);spec.loader.exec_module(gui)
class GuiTests(unittest.TestCase):
 def test_command_is_argument_list(self):
  cmd=gui.command('install','native','br');self.assertEqual(cmd[-2:],['--region','br']);self.assertIn('--backend',cmd)
 def test_terminal_uses_exec_args(self):
  with patch.object(gui.shutil,'which',side_effect=lambda n:'/usr/bin/konsole' if n=='konsole' else None):
   self.assertEqual(gui.in_terminal(['python3','a path/script.py']),['/usr/bin/konsole','--hold','-e','python3','a path/script.py'])
 def test_missing_terminal_errors(self):
  with patch.object(gui.shutil,'which',return_value=None),self.assertRaises(RuntimeError):gui.in_terminal(['python3'])
 def test_rejects_untrusted_region(self):
  with self.assertRaises(ValueError):gui.command('run','native','br;echo secret')
if __name__=='__main__':unittest.main()
