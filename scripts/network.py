import socket
import psutil
from scripts import utils, db

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

def kill_process(pid):
    try:
        p = psutil.Process(pid)
        print(f"Killing {p.name()} (PID {pid})")
        p.terminate()
        p.wait(timeout=5)
        print("Process terminated.")
    except Exception as e:
        print(f"Failed: {e}")

def scan_network(db_path):
    try:
        for conn in psutil.net_connections(kind='inet'):
            pid = conn.pid
            name = "Unknown"
            exe = "Unknown"
            local = (conn.laddr.ip, conn.laddr.port) if conn.laddr else "N/A"
            remote = (conn.raddr.ip, conn.raddr.port) if conn.raddr else "N/A"
            status = conn.status

            try:
                if pid:
                    p = psutil.Process(pid)
                    name = p.name()
                    exe = p.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
            try:
                db.update_connection(
                        db_path,
                        name = name,
                        path = exe,
                        timestamp = utils.get_current_time(),
                        local_port = local[1] if local != "N/A" else 0,
                        remote_ip = remote[0] if remote != "N/A" else "",
                        remote_port = remote[1] if remote != "N/A" else 0,
                        status = status
                    )
            except Exception as e:
                utils.log_error(f"Error updating database: {str(e)}")
            
            connection = db.get_connection(db_path, name)
            whitelisted = connection[7]
            blacklisted = connection[8]
            utils.log_info(
                f"{name} ({exe}) | Local: {local} | Remote: {remote} | Status: {status} | "
                f"{'BLACKLISTED' if blacklisted and not whitelisted else 'WHITELISTED' if whitelisted and not blacklisted else 'UNKNOWN'}"
            )

            if blacklisted and not whitelisted:
                utils.log_warning("  > Blacklisted connection will be killed")
            if whitelisted and not blacklisted:
                utils.log_info("  > Whitelisted connection will be ignored")
            if not whitelisted and not blacklisted:
                utils.log_info("  > Unknown connection: consider whitelisting or blacklisting")

                

    except Exception as e:
        print(f"Error scanning network: {str(e)}")