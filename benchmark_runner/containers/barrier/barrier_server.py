import socket
import time
import sys

port = int(sys.argv[1])
vm_count = int(sys.argv[2])
timeout = int(sys.argv[3])
result_path = sys.argv[4] if len(sys.argv) > 4 else ''
LEAD = 15.0

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('0.0.0.0', port))
srv.listen(512)

registered = set()
told = set()
start = time.time()
t0 = 0.0
polls = 0

while True:
    now = time.time()
    if now - start > timeout:
        break
    if t0 and now > t0 + 20 and registered.issubset(told):
        break
    srv.settimeout(1.0)
    try:
        conn, addr = srv.accept()
    except socket.timeout:
        continue
    polls += 1
    ip = addr[0]
    try:
        conn.settimeout(3)
        data = b''
        while b'\n' not in data and len(data) < 256:
            c = conn.recv(256)
            if not c:
                break
            data += c
        registered.add(ip)
        if not t0 and len(registered) >= vm_count:
            t0 = time.time() + LEAD
        if t0:
            conn.sendall(f'GO {t0:.3f}\n'.encode())
            told.add(ip)
        else:
            conn.sendall(b'WAIT\n')
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass

srv.close()

if result_path:
    with open(result_path, 'w') as f:
        f.write(str(len(registered)))

print(f'BARRIER_START_EPOCH:{t0:.3f}')
print(f'BARRIER_POLLS:{polls}')
print(f'BARRIER_TOLD:{len(told)}')
print(f'BARRIER_RESULT:{len(registered)}')
