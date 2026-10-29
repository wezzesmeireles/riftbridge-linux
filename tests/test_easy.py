import importlib.util,io,unittest
from pathlib import Path
from contextlib import redirect_stdout,redirect_stderr
from unittest.mock import patch
s=importlib.util.spec_from_file_location('easy',Path(__file__).resolve().parents[1]/'scripts/easy.py');easy=importlib.util.module_from_spec(s);s.loader.exec_module(easy)
class EasyTests(unittest.TestCase):
 def invoke(self,args):
  with redirect_stdout(io.StringIO()) as out,redirect_stderr(io.StringIO()):result=easy.main(args)
  return result,out.getvalue()
 def test_preview_never_executes(self):
  for b in ('native','nix'):
   with patch.object(easy.subprocess,'run',side_effect=AssertionError('must not execute')):
    code,text=self.invoke(['install','--backend',b,'--dry-run']);self.assertEqual(code,0);self.assertIn('RCLOL_REGION=BR',text)
 def test_privilege_scope(self):
  commands=easy.plan('install','native','br');self.assertEqual(commands[-1],['sh','scripts/installer.sh','br']);self.assertEqual([c for c in commands if c[0]=='sudo'],[['sudo','cmake','--install','build/darling-src/build']])
 def test_invalid_region(self):
  with self.assertRaises(SystemExit),redirect_stderr(io.StringIO()):easy.main(['install','--region','br;evil'])
 def test_invalid_jobs(self):
  with self.assertRaises(SystemExit),redirect_stderr(io.StringIO()):easy.main(['install','--jobs','0','--dry-run'])
 def test_unsupported_arch(self):
  with patch.object(easy.platform,'machine',return_value='aarch64'),self.assertRaises(SystemExit),redirect_stderr(io.StringIO()):easy.main(['install','--dry-run'])
 def test_run_env(self):
  with patch.object(easy.os,'geteuid',return_value=1000),patch.object(easy.subprocess,'run') as run:
   self.invoke(['run','--backend','native','--region','na']);self.assertEqual(run.call_args.kwargs['env']['RCLOL_LOCALE'],'en_US')
 def test_failure_stops(self):
  with patch.object(easy.os,'geteuid',return_value=1000),patch.object(easy.subprocess,'run',side_effect=OSError('missing')) as run:
   self.assertEqual(self.invoke(['doctor','--backend','native'])[0],1);self.assertEqual(run.call_count,1)
if __name__=='__main__':unittest.main()
