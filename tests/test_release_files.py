"""Host-only integrity and interrupted-transfer tests. No network or phone I/O."""
import hashlib, importlib.util, io, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release_files',root/'tools/release_files.py')
tool=importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

def item(name,data):
    return dict(name=name,size=len(data),sha256=hashlib.sha256(data).hexdigest())

class ReleaseFiles(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)
        parts=[b'first',b'second',b'third']
        assets=[]
        for i,data in enumerate(parts,1):
            name=f'firmware.kdz.part{i:02d}'
            (self.directory/name).write_bytes(data)
            assets.append(item(name,data))
        self.manifest=dict(reassembled_kdz=item('firmware.kdz',b''.join(parts)),assets=assets)

    def test_reassemble_and_reuse_verified(self):
        p=tool.assemble(self.directory,self.manifest)
        self.assertEqual(p.read_bytes(),b'firstsecondthird')
        self.assertEqual(tool.assemble(self.directory,self.manifest),p)

    def test_corrupt_part_stops_before_output(self):
        (self.directory/'firmware.kdz.part02').write_bytes(b'broken')
        with self.assertRaises(ValueError): tool.assemble(self.directory,self.manifest)
        self.assertFalse((self.directory/'firmware.kdz').exists())
        self.assertFalse((self.directory/'firmware.kdz.assembling').exists())

    def test_existing_output_never_overwritten(self):
        p=self.directory/'firmware.kdz'
        p.write_bytes(b'keep this original')
        with self.assertRaises(ValueError): tool.assemble(self.directory,self.manifest)
        self.assertEqual(p.read_bytes(),b'keep this original')

    def test_stale_partial_needs_explicit_restart(self):
        partial=self.directory/'firmware.kdz.assembling'
        partial.write_bytes(b'partial')
        with self.assertRaises(FileExistsError): tool.assemble(self.directory,self.manifest)
        self.assertEqual(partial.read_bytes(),b'partial')
        tool.assemble(self.directory,self.manifest,restart=True)
        self.assertFalse(partial.exists())

    def prepare_download(self):
        repo=self.directory/'repo'
        (repo/'downloads').mkdir(parents=True)
        manifest=dict(repository='example/example',tag='test',assets=[item('asset.bin',b'complete')])
        (repo/'downloads/manifest.json').write_text(json.dumps(manifest))
        downloads=self.directory/'downloads'
        downloads.mkdir()
        return repo, downloads, ['release_files.py','download','--directory',str(downloads)]

    def test_interrupted_download_cleans_own_partial_then_retries(self):
        repo,directory,args=self.prepare_download()
        class Broken(io.BytesIO):
            calls=0
            def read(self,n=-1):
                self.calls+=1
                if self.calls>1: raise OSError('simulated disconnect')
                return b'partial'
        with patch.object(tool,'ROOT',repo),patch('sys.argv',args),patch.object(tool.urllib.request,'urlopen',return_value=Broken()):
            with self.assertRaises(OSError): tool.main()
        self.assertFalse((directory/'asset.bin.downloading').exists())
        with patch.object(tool,'ROOT',repo),patch('sys.argv',args),patch.object(tool.urllib.request,'urlopen',return_value=io.BytesIO(b'complete')):
            tool.main()
        self.assertEqual((directory/'asset.bin').read_bytes(),b'complete')

    def test_creation_race_preserves_other_transfer(self):
        repo,directory,args=self.prepare_download()
        temp=directory/'asset.bin.downloading'
        class OtherTransfer(io.BytesIO):
            def __enter__(self):
                temp.write_bytes(b'another transfer')
                return self
        with patch.object(tool,'ROOT',repo),patch('sys.argv',args),patch.object(tool.urllib.request,'urlopen',return_value=OtherTransfer(b'complete')):
            with self.assertRaises(FileExistsError): tool.main()
        self.assertEqual(temp.read_bytes(),b'another transfer')

if __name__=='__main__':
    unittest.main()
