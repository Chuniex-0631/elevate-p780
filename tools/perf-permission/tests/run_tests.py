"""Host-only mock tests. They do NOT establish perf access on Android."""
import os, pathlib, subprocess, tempfile
root=pathlib.Path(__file__).resolve().parents[1]
expected={'pass':(0,'USER_COUNT_PASS'),'denied':(10,'OPEN_DENIED'),
 'unsupported':(10,'OPEN_ERROR'),'context':(65,'WRONG_CONTEXT'),
 'enable':(11,'CONTROL_ERROR'),'zero':(13,'OPEN_OK_COUNT_INCONCLUSIVE'),
 'short':(12,'READ_ERROR'),'readerror':(12,'READ_ERROR')}
with tempfile.TemporaryDirectory() as d:
 binary=str(pathlib.Path(d)/'probe-mock')
 wraps=['getuid','geteuid','syscall','ioctl','read','close']
 subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror',str(root/'perf_permission.c'),
  str(root/'tests/mock_io.c'),*[f'-Wl,--wrap={x}' for x in wraps],'-o',binary],check=True)
 for mode,(rc,result) in expected.items():
  p=subprocess.run([binary],env={**os.environ,'MOCK_MODE':mode},capture_output=True,text=True,timeout=6)
  assert p.returncode==rc,(mode,p.returncode,p.stdout,p.stderr)
  assert f'result={result}\n' in p.stdout,(mode,p.stdout)
  if mode in ['pass','zero','short','readerror']: assert 'close=PASS\n' in p.stdout
  print(f'{mode}: PASS ({result})')
print('8 host-mock cases passed. NOT an Android/device test.')
