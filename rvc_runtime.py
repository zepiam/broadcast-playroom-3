"""Read-only, per-engine RVC runtime configuration; respects an explicit CPU choice."""
from __future__ import annotations
import json, os
from pathlib import Path
from types import SimpleNamespace


def create_inference(model_path, device):
    import torch
    import rvc_python
    from rvc_python.infer import RVCInference
    from rvc_python.modules.vc.modules import VC
    library=Path(rvc_python.__file__).resolve().parent
    missing=[name for name in ('hubert_base.pt','rmvpe.pt') if not (library/'base_model'/name).is_file()]
    if missing:raise RuntimeError('ไฟล์ประกอบ RVC ของรุ่น FULL ไม่ครบ: '+', '.join(missing))
    chosen=str(device)
    gpu_name=None;gpu_mem=None;half=False
    if chosen.startswith('cuda'):
        try:
            index=int(chosen.split(':')[-1]) if ':' in chosen else 0
            if not torch.cuda.is_available() or index>=torch.cuda.device_count():raise RuntimeError('No GPU')
            torch.empty(1,device=chosen)
            gpu_name=torch.cuda.get_device_name(index)
            gpu_mem=torch.cuda.get_device_properties(index).total_memory/1073741824
            half=not any(token in gpu_name.upper() for token in ('GTX 16','P40','P10','1060','1070','1080'))
        except Exception:chosen='cpu'
    else:chosen='cpu'
    configs={}
    for file in (library/'configs').rglob('*.json'):
        value=json.loads(file.read_text(encoding='utf-8'))
        if not half and isinstance(value.get('train'),dict):value['train']['fp16_run']=False
        configs[file.relative_to(library/'configs').as_posix()]=value
    limits=(3,10,60,65) if half else (1,6,38,41)
    if gpu_mem is not None and gpu_mem<=4:limits=(1,5,30,32)
    config=SimpleNamespace(lib_dir=str(library),device=chosen,is_half=half,use_jit=False,n_cpu=max(1,min(4,os.cpu_count() or 1)),gpu_name=gpu_name,gpu_mem=gpu_mem,json_config=configs,dml=False,instead='',x_pad=limits[0],x_query=limits[1],x_center=limits[2],x_max=limits[3])
    class LocalInference(RVCInference):
        def __init__(self):
            self.models_dir=str(Path(model_path).parent);self.device=chosen;self.lib_dir=str(library)
            self.config=config;self.vc=VC(self.lib_dir,config);self.current_model=None;self.models={}
            self.f0method='rmvpe';self.f0up_key=0;self.index_rate=.75;self.filter_radius=3;self.resample_sr=0;self.rms_mix_rate=.25;self.protect=.33
            self.load_model(str(model_path),version='v2')
    return LocalInference()
