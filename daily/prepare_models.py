from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
from urllib.request import urlopen

root=Path(__file__).resolve().parent.parent/'output/models'
root.mkdir(parents=True,exist_ok=True)
base='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'
files={'kokoro-v1.0.onnx':'7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5',
       'voices-v1.0.bin':'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d'}
def fetch(item):
    name,sha=item; target=root/name
    if not target.exists():
        with urlopen(base+name,timeout=60) as response, target.with_suffix('.part').open('wb') as dest:
            while chunk:=response.read(1024*1024): dest.write(chunk)
        target.with_suffix('.part').replace(target)
    with target.open('rb') as file: actual=hashlib.file_digest(file,'sha256').hexdigest()
    if actual!=sha: raise ValueError(f'Checksum mismatch: {name}')
    return {'file':name,'sha256':actual,'bytes':target.stat().st_size}
with ThreadPoolExecutor(max_workers=2) as pool:
    for result in pool.map(fetch,files.items()): print(result,flush=True)
