$ErrorActionPreference = 'Stop'

$stressDir = 'C:\tools\stress'
$pythonExe = @('C:\Python312\python.exe', 'C:\Program Files\Python312\python.exe') | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $pythonExe) { $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source }
if (-not $pythonExe) { throw 'python.exe not found in the Windows guest' }
$stressScript = "$stressDir\stress.py"
$reportFile = "$stressDir\stress_report.json"

New-Item -ItemType Directory -Force -Path $stressDir | Out-Null
Remove-Item -Path $reportFile -Force -ErrorAction SilentlyContinue

$ErrorActionPreference = 'Continue'
& $pythonExe -c "import numpy, psutil" *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "numpy/psutil not present, installing"
    & $pythonExe -m pip install --quiet --no-input numpy psutil *> $null
    & $pythonExe -c "import numpy, psutil" *> $null
    if ($LASTEXITCODE -ne 0) { throw "numpy/psutil unavailable and pip install failed - bake them into the Windows image" }
    Write-Host "numpy installed"
}
$ErrorActionPreference = 'Stop'

$scriptContent = @"
import multiprocessing, time, psutil, json, datetime, socket
import numpy as np

MEM_BUFFER_MB = {{ mem_buffer_mb }}
BLOCK_BYTES = {{ block_bytes | default(64) }}
STRIDE = {{ stride | default(1111) }}
BARRIER_HOST = 'winstress-barrier-{{ trunc_uuid }}'
BARRIER_PORT = {{ barrier_port | default(29999) }}
BARRIER_TIMEOUT = {{ barrier_timeout | default(3600) }}

barrier_stats = {'attempts': 0, 'errors': [], 'connected_at': 0, 'released_at': 0, 'start_epoch': 0, 'late_by': 0}

PROGRESS = r'C:\tools\stress\progress.txt'

def mark(tag):
    try:
        with open(PROGRESS, 'a') as _pf:
            _pf.write(datetime.datetime.utcnow().isoformat() + ' ' + str(tag) + '\n')
            _pf.flush()
    except Exception:
        pass

def wait_barrier(host, port, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        barrier_stats['attempts'] += 1
        try:
            s = socket.create_connection((host, port), timeout=10)
            if not barrier_stats['connected_at']:
                barrier_stats['connected_at'] = time.time()
            s.sendall((socket.gethostname() + '\n').encode())
            s.settimeout(5)
            _buf = b''
            while b'\n' not in _buf and len(_buf) < 64:
                _c = s.recv(64)
                if not _c:
                    break
                _buf += _c
            try:
                s.close()
            except Exception:
                pass
            _p = _buf.decode(errors='ignore').strip().split()
            if len(_p) >= 2 and _p[0] == 'GO':
                _now = time.time()
                _t0 = _now + float(_p[2]) if len(_p) >= 3 else float(_p[1])
                if _t0 - _now > 120:
                    _t0 = _now
                barrier_stats['released_at'] = time.time()
                barrier_stats['start_epoch'] = _t0
                barrier_stats['late_by'] = round(max(0.0, time.time() - _t0), 3)
                while time.time() < _t0:
                    time.sleep(min(0.02, max(0.0, _t0 - time.time())))
                return True
            time.sleep(1.0)
        except Exception as _e:
            if len(barrier_stats['errors']) < 20:
                barrier_stats['errors'].append(f'{time.time():.1f} {type(_e).__name__}: {_e}')
            time.sleep(1.0)
    return False

def burn_cpu(d, result_dict, idx, ready, go, bucket_sec=10):
    size = (MEM_BUFFER_MB * 1024 * 1024) // 8
    block_size = max(1, BLOCK_BYTES // 8)
    stride = STRIDE
    if stride <= block_size:
        stride = block_size * 8 + 1
    if stride % 2 == 0:
        stride += 1
    rng = np.random.default_rng()
    array = rng.integers(0, (1 << 64) - 1, size=size, dtype=np.uint64)
    dest = np.zeros(size, dtype=np.uint64)
    dest[:] = 1
    batch = max(1, 65536 // block_size)
    bytes_per_copy = block_size * 8
    mark('w' + str(idx) + '_alloc_done')
    with ready.get_lock():
        ready.value += 1
    mark('w' + str(idx) + '_waiting_go')
    go.wait()
    mark('w' + str(idx) + '_go_released')
    stress_start = datetime.datetime.utcnow().isoformat()
    start = time.perf_counter()
    end = start + d
    ops = 0
    buckets = []
    next_bucket_at = start + bucket_sec
    bucket_start_ops = 0
    bucket_start_time = start
    c = 0
    stop = False
    while not stop:
        for _ in range(batch):
            dest[c:c + block_size] = array[c:c + block_size]
            c = (c + stride) % size
        ops += batch * bytes_per_copy
        now = time.perf_counter()
        if now >= end:
            stop = True
        if now >= next_bucket_at or stop:
            b_ops = ops - bucket_start_ops
            b_elapsed = now - bucket_start_time
            buckets.append({'ops': b_ops, 'elapsed': b_elapsed, 'ops_per_sec': b_ops / b_elapsed if b_elapsed > 0 else 0})
            bucket_start_ops = ops
            bucket_start_time = now
            next_bucket_at = now + bucket_sec
    final_now = time.perf_counter()
    if final_now > bucket_start_time:
        b_ops = ops - bucket_start_ops
        b_elapsed = final_now - bucket_start_time
        buckets.append({'ops': b_ops, 'elapsed': b_elapsed, 'ops_per_sec': b_ops / b_elapsed if b_elapsed > 0 else 0})
    elapsed = time.perf_counter() - start
    mark('w' + str(idx) + '_loop_done ops=' + str(ops))
    result_dict[idx] = {'ops': ops, 'elapsed': elapsed, 'ops_per_sec': ops / elapsed, 'buckets': buckets, 'stress_start_utc': stress_start}
    mark('w' + str(idx) + '_result_stored')

def burn_memory(target_percent, duration, go=None):
    total = psutil.virtual_memory().total
    target_bytes = int(total * target_percent / 100)
    current_used = psutil.virtual_memory().used
    alloc_bytes = target_bytes - current_used
    if alloc_bytes <= 0:
        print(f'Memory already at {psutil.virtual_memory().percent}%, skipping')
        return
    chunk_size = 100 * 1024 * 1024
    blocks = []
    allocated = 0
    while allocated < alloc_bytes:
        size = min(chunk_size, alloc_bytes - allocated)
        blocks.append(bytearray(size))
        allocated += size
    print(f'Memory at {psutil.virtual_memory().percent}%, holding for {duration}s')
    if go is not None:
        go.wait()
    time.sleep(duration)

def steal_time():
    try:
        return float(getattr(psutil.cpu_times(), 'steal', 0.0) or 0.0)
    except Exception:
        return 0.0

if __name__ == '__main__':
    multiprocessing.freeze_support()
    try:
        import os as _os
        _os.remove(PROGRESS)
    except Exception:
        pass
    mark('main_start')
    run_start_time = datetime.datetime.utcnow().isoformat()
    cpu_total = multiprocessing.cpu_count()
    cpu_count = max(1, int(cpu_total * {{ stress_cpu }} / 100))
    duration = {{ stress_duration }}
    mem_target = {{ stress_memory }}

    print(f'CPU count: {cpu_total}')
    print(f'Stressing {cpu_count} CPUs and {mem_target}% memory for {duration}s')
    print(f'Total memory: {psutil.virtual_memory().total // (1024**2)}MB')
    print(f'Block {BLOCK_BYTES}B stride {STRIDE} buffer {MEM_BUFFER_MB}MB')

    manager = multiprocessing.Manager()
    result_dict = manager.dict()
    ready = multiprocessing.Value('i', 0)
    go = multiprocessing.Event()

    mem_proc = None
    if mem_target > 0:
        mem_proc = multiprocessing.Process(target=burn_memory, args=(mem_target, duration, go))
        mem_proc.start()

    cpu_procs = [multiprocessing.Process(target=burn_cpu, args=(duration, result_dict, i, ready, go)) for i in range(cpu_count)]
    [p.start() for p in cpu_procs]
    mark('workers_started n=' + str(cpu_count))

    while ready.value < cpu_count:
        time.sleep(0.2)
    mark('all_allocated')

    print(f'All {cpu_count} workers allocated, connecting to barrier')
    _steal_before = steal_time()
    _t_before = time.time()
    mark('barrier_enter host=' + str(BARRIER_HOST))
    _br = wait_barrier(BARRIER_HOST, BARRIER_PORT, BARRIER_TIMEOUT)
    mark('barrier_exit ok=' + str(_br) + ' attempts=' + str(barrier_stats['attempts']) + ' t0=' + str(barrier_stats['start_epoch']))
    _steal_after = steal_time()
    _t_after = time.time()
    stress_start_time = datetime.datetime.utcnow().isoformat()
    go.set()
    mark('go_set')
    print(f'Barrier released, stress start {stress_start_time}')

    intervals = max(1, duration // 30)
    samples = []
    for i in range(intervals):
        time.sleep(30)
        mem = psutil.virtual_memory()
        cpu_pct = psutil.cpu_percent(interval=1)
        sample = {
            'time_sec': (i+1)*30,
            'cpu_percent': cpu_pct,
            'mem_percent': mem.percent,
            'mem_used_mb': round(mem.used / (1024**2), 1),
            'mem_total_mb': round(mem.total / (1024**2), 1),
            'mem_used_gb': round(mem.used / (1024**3), 1),
            'mem_total_gb': round(mem.total / (1024**3), 1)
        }
        samples.append(sample)
        print(f"At {sample['time_sec']}s: CPU={cpu_pct}% MEM={mem.percent}%")

    mark('sampling_done')
    [p.join() for p in cpu_procs]
    mark('workers_joined')
    if mem_proc:
        mem_proc.join()

    total_ops = sum(r['ops'] for r in result_dict.values())
    total_ops_per_sec = sum(r['ops_per_sec'] for r in result_dict.values())
    avg_ops_per_sec = total_ops_per_sec / cpu_count if cpu_count > 0 else 0

    print(f'Total operations: {total_ops:,}')
    print(f'Total throughput: {total_ops_per_sec:,.0f} ops/sec')

    run_end_time = datetime.datetime.utcnow().isoformat()
    report = {
        'config': {
            'cpu_total': cpu_total,
            'cpu_stressed': cpu_count,
            'stress_cpu_percent': {{ stress_cpu }},
            'stress_memory_percent': mem_target,
            'duration_sec': duration,
            'block_bytes': BLOCK_BYTES,
            'stride': STRIDE,
            'mem_buffer_mb': MEM_BUFFER_MB,
            'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 1),
            'total_memory_mb': round(psutil.virtual_memory().total / (1024**2), 1),
            'run_start_time_utc': run_start_time,
            'run_end_time_utc': run_end_time,
            'stress_start_time_utc': stress_start_time,
            'steal_before_barrier': _steal_before,
            'steal_after_barrier': _steal_after,
            'barrier_wait_sec': round(_t_after - _t_before, 3),
            'barrier_connected_at': barrier_stats['connected_at'],
            'barrier_released_at': barrier_stats['released_at'],
            'barrier_attempts': barrier_stats['attempts'],
            'barrier_errors': barrier_stats['errors'],
            'barrier_start_epoch': barrier_stats['start_epoch'],
            'barrier_late_by': barrier_stats['late_by']
        },
        'throughput': {
            'total_ops': total_ops,
            'total_ops_per_sec': round(total_ops_per_sec, 2),
            'avg_ops_per_cpu': round(avg_ops_per_sec, 2),
            'per_cpu': [{'cpu': i, 'ops': r['ops'], 'ops_per_sec': round(r['ops_per_sec'], 2),
                         'buckets': [{'ops': b['ops'], 'elapsed': round(b['elapsed'], 3), 'ops_per_sec': round(b['ops_per_sec'], 2)} for b in r.get('buckets', [])]}
                        for i, r in sorted(result_dict.items())]
        },
        'samples': samples
    }

    with open(r'C:\tools\stress\stress_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    mark('report_written ops=' + str(total_ops))
    print('Done')
"@

Set-Content -Path $stressScript -Value $scriptContent -Force
Write-Host "Launching stress test detached"
$batPath = "$stressDir\run_stress.bat"
$batBody = '"' + $pythonExe + '" -u "' + $stressScript + '" > "' + $stressDir + '\stress.log" 2> "' + $stressDir + '\stress.err"'
Set-Content -Path $batPath -Value @('@echo off', $batBody) -Encoding ascii
$spawn = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = ('cmd.exe /c "' + $batPath + '"')}
if ($spawn.ReturnValue -ne 0) { throw "Win32_Process Create failed rc=$($spawn.ReturnValue)" }
Start-Sleep -Seconds 5
if (-not (Get-Process -Id $spawn.ProcessId -ErrorAction SilentlyContinue)) { throw "stress launcher exited immediately - check $stressDir\stress.err" }
Write-Host "Stress test launched pid $($spawn.ProcessId)"
