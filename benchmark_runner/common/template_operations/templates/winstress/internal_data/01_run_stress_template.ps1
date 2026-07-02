$ErrorActionPreference = 'Stop'

$stressDir = 'C:\tools\stress'
$pythonExe = 'C:\Program Files\Python312\python.exe'
$stressScript = "$stressDir\stress.py"
$reportFile = "$stressDir\stress_report.json"

New-Item -ItemType Directory -Force -Path $stressDir | Out-Null

$scriptContent = @"
import multiprocessing, time, psutil, json

def burn_cpu(d, result_dict, idx):
    ops = 0
    start = time.time()
    end = start + d
    while time.time() < end:
        _ = 2**32
        ops += 1
    elapsed = time.time() - start
    result_dict[idx] = {'ops': ops, 'elapsed': elapsed, 'ops_per_sec': ops / elapsed}

def burn_memory(target_percent, duration):
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
        print(f'Allocated {allocated // (1024*1024)}MB / {alloc_bytes // (1024*1024)}MB ({psutil.virtual_memory().percent}%)')
    print(f'Memory at {psutil.virtual_memory().percent}%, holding for {duration}s...')
    time.sleep(duration)

if __name__ == '__main__':
    cpu_total = multiprocessing.cpu_count()
    cpu_count = max(1, int(cpu_total * {{ stress_cpu }} / 100))
    duration = {{ stress_duration }}
    mem_target = {{ stress_memory }}

    print(f'CPU count: {cpu_total}')
    print(f'Stressing {cpu_count} CPUs ({{"{{ stress_cpu }}"}}%) and {mem_target}% memory for {duration}s')
    print(f'Total memory: {psutil.virtual_memory().total // (1024**3)}GB')
    print(f'Memory before: {psutil.virtual_memory().percent}%')
    print(f'CPU before: {psutil.cpu_percent(interval=1)}%')

    mem_proc = None
    if mem_target > 0:
        mem_proc = multiprocessing.Process(target=burn_memory, args=(mem_target, duration))
        mem_proc.start()
        time.sleep(5)

    manager = multiprocessing.Manager()
    result_dict = manager.dict()

    cpu_procs = [multiprocessing.Process(target=burn_cpu, args=(duration, result_dict, i)) for i in range(cpu_count)]
    [p.start() for p in cpu_procs]

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
            'mem_used_gb': round(mem.used / (1024**3), 1),
            'mem_total_gb': round(mem.total / (1024**3), 1)
        }
        samples.append(sample)
        print(f"At {sample['time_sec']}s: CPU={cpu_pct}% MEM={mem.percent}% ({sample['mem_used_gb']}GB/{sample['mem_total_gb']}GB)")

    [p.join() for p in cpu_procs]
    if mem_proc:
        mem_proc.join()

    total_ops = sum(r['ops'] for r in result_dict.values())
    total_ops_per_sec = sum(r['ops_per_sec'] for r in result_dict.values())
    avg_ops_per_sec = total_ops_per_sec / cpu_count if cpu_count > 0 else 0

    print(f'CPU after: {psutil.cpu_percent(interval=1)}%')
    print(f'Memory after: {psutil.virtual_memory().percent}%')
    print(f'Total operations: {total_ops:,}')
    print(f'Total throughput: {total_ops_per_sec:,.0f} ops/sec')
    print(f'Avg per CPU: {avg_ops_per_sec:,.0f} ops/sec')

    report = {
        'config': {
            'cpu_total': cpu_total,
            'cpu_stressed': cpu_count,
            'stress_cpu_percent': {{ stress_cpu }},
            'stress_memory_percent': mem_target,
            'duration_sec': duration,
            'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 1)
        },
        'throughput': {
            'total_ops': total_ops,
            'total_ops_per_sec': round(total_ops_per_sec, 2),
            'avg_ops_per_cpu': round(avg_ops_per_sec, 2),
            'per_cpu': [{'cpu': i, 'ops': r['ops'], 'ops_per_sec': round(r['ops_per_sec'], 2)} for i, r in sorted(result_dict.items())]
        },
        'samples': samples
    }

    with open(r'C:\tools\stress\stress_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print('Report saved to C:\\tools\\stress\\stress_report.json')
    print('Done')
"@

Set-Content -Path $stressScript -Value $scriptContent -Force
Write-Host "Running stress test..."
& $pythonExe $stressScript
Write-Host "Stress test complete"
