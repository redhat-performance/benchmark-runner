import socket
import time
import sys

port = int(sys.argv[1])
vm_count = int(sys.argv[2])
timeout = int(sys.argv[3])
result_path = sys.argv[4] if len(sys.argv) > 4 else ''

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('0.0.0.0', port))
srv.listen(vm_count + 10)

conns = []
start = time.time()
try:
    while len(conns) < vm_count:
        remaining = timeout - (time.time() - start)
        if remaining <= 0:
            break
        srv.settimeout(remaining)
        try:
            conn, addr = srv.accept()
            conns.append(conn)
        except socket.timeout:
            break
finally:
    srv.close()

if result_path:
    with open(result_path, 'w') as f:
        f.write(str(len(conns)))

# Printed as the last line so callers without a shared filesystem (e.g. a
# Kubernetes pod, whose result is read back via `oc logs`) can parse it.
print(f'BARRIER_RESULT:{len(conns)}')
