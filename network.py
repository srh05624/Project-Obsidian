import socket
import logger
import psutil
import threading

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_listeners():
    listeners = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == psutil.CONN_LISTEN and conn.laddr:
            pid = conn.pid
            name = "Unknown"
            exe = "Unknown"
            try:
                if pid:
                    p = psutil.Process(pid)
                    name = p.name()
                    exe = p.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

            listeners.append({
                "ip": conn.laddr.ip,
                "port": conn.laddr.port,
                "pid": pid,
                "name": name,
                "exe": exe
            })
    return listeners

def kill_pid(pid):
    try:
        p = psutil.Process(pid)
        print(f"Killing {p.name()} (PID {pid})")
        p.terminate()
        p.wait(timeout=5)
        print("Process terminated.")
    except Exception as e:
        print(f"Failed: {e}")