import psutil, socket, subprocess
from scripts import alerts, utils, db

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

def get_actual_port(pid):
    try:
        output = subprocess.check_output(f"ss -lntp | grep {pid}", shell=True).decode()
        # Parse the output to extract the port from something like 127.0.0.1:44321
        print(f"Actual port info:\n{output}")
    except Exception as e:
        print(f"Could not determine port: {e}")

def kill_process(pid):
    try:
        p = psutil.Process(pid)
        utils.log_info(f"Killing {p.name()} (PID {pid})")
        p.terminate()
        p.wait(timeout=5)
        utils.log_info(f"Process terminated.")
    except Exception as e:
        utils.log_error(f"Failed: {e}")

async def scan_network(db_path, alerts_enabled=False):
    try:
        utils.log_info(f"[{utils.get_current_time()}] Starting network scan...")
        
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
                        pid = pid,
                        local_port = local[1] if local != "N/A" else 0,
                        remote_ip = remote[0] if remote != "N/A" else "",
                        remote_port = remote[1] if remote != "N/A" else 0,
                        status = status
                    )
            except Exception as e:
                utils.log_error(f"Error updating database: {str(e)}")
            
            connection = db.get_connection(db_path, name)
            blacklisted = connection[-2]
            whitelisted = connection[-1]

            utils.log_info(f"Connection: {name} {"blacklisted" if blacklisted else "whitelisted" if whitelisted else "unknown"}")

            if blacklisted and not whitelisted:
                utils.log_warning("  > Blacklisted connection detected!")
            if not whitelisted and not blacklisted:
                if alerts_enabled:
                    utils.log_info("  > Alerting user about suspicious connection...")
                    
                    choice = await alerts.alert_user(
                        f"Suspicious connection detected**\n" +
                        f"Process: {name}\n" + f"PID: {pid}\n" +
                        f"Path: `{exe}`\n" +
                        f"Remote: `{remote[0]}:{remote[1]}`\n"
                    )

                    
                    if choice == "Whitelist":
                        db.update_connection(db.db_path, name, blacklisted=0, whitelisted=1)
                    elif choice == "Blacklist":
                        db.update_connection(db.db_path, name, blacklisted=1, whitelisted=0)
                    elif choice == "Kill Once":
                        db.update_connection(db.db_path, name, blacklisted=0, whitelisted=0)
                        if pid != 0:
                            kill_process(pid)
                
    except Exception as e:
        utils.log_error(f"Error scanning network: {str(e)}")