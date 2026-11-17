"""Report compute capabilities without dumping environment variables or credentials."""
import importlib.util,json,platform,shutil,subprocess
from pathlib import Path
data={"system":platform.system(),"release":platform.release(),"machine":platform.machine(),
    "python":platform.python_version(),"cpu_count":__import__("os").cpu_count(),
    "packages":{p:bool(importlib.util.find_spec(p)) for p in ("numpy","scipy","cv2","torch","PIL","pyproj","shapely")}}
if shutil.which("nvidia-smi"):
    p=subprocess.run(["nvidia-smi","--query-gpu=name,memory.total,driver_version","--format=csv,noheader"],
        capture_output=True,text=True,timeout=20)
    data["gpu"]=p.stdout.strip() if p.returncode==0 else "query_failed"
else:data["gpu"]=None
Path("results").mkdir(exist_ok=True)
Path("results/runner.json").write_text(json.dumps(data,indent=2)+"\n")
print("RUNNER_CAPABILITIES "+json.dumps(data))
