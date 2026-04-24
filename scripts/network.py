from scripts import alerts, utils, db
import psutil, socket, subprocess, ipaddress

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

def is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        utils.log_warning(f"Invalid IP address: {ip}")
        return False

def get_actual_port(pid):
    try:
        output = subprocess.check_output(f"ss -lntp | grep {pid}", shell=True).decode()
        # Parse the output to extract the port from something like 127.0.0.1:44321
        utils.log_info(f"Actual port info:\n{output}")
    except Exception as e:
        utils.log_error(f"Could not determine port: {e}")

def kill_process(pid):
    try:
        p = psutil.Process(pid)
        utils.log_info(f"Killing {p.name()} (PID {pid})")
        try:
            p.terminate()
            p.wait(timeout=5)
            utils.log_info(f"Process terminated gracefully.")
        except Exception as e:
            utils.log_warning(f"Graceful termination failed: {e}. Forcing kill.")
            p.kill()
            p.wait(timeout=5)
            utils.log_info(f"Process killed forcefully.")
    except Exception as e:
        utils.log_error(f"Failed to kill process {pid}! Error: {e}")

async def scan_network(config):
    try:
        utils.log_info(f"Starting network scan...")

        try:
            connections = psutil.net_connections(kind='inet')
        except psutil.AccessDenied:
            # Fallback to process_iter() if net_connections fails
            connections = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Add connections for each process
                    connections.extend(proc.connections(kind='inet'))
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        
        for conn in connections:
            pid = conn.pid
            name = "Unknown"
            exe = "Unknown"
            local = (conn.laddr.ip, conn.laddr.port) if conn.laddr else "N/A"
            local_port = local[1] if local != "N/A" else 0
            remote = (conn.raddr.ip, conn.raddr.port) if conn.raddr else "N/A"
            remote_ip = remote[0] if remote != "N/A" else ""
            remote_port = remote[1] if remote != "N/A" else 0
            status = conn.status
            
            try:
                if pid:
                    p = psutil.Process(pid)
                    name = p.name()
                    exe = p.exe()
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                utils.log_warning(f"Process with PID {pid} no longer exists.")
            except psutil.AccessDenied as e:
                utils.log_warning(f"Access denied when trying to get process info for PID {pid}: {e}")
            
            key = exe + str(remote_ip) + str(remote_port)

            if name == "Unknown" and pid == 0 and exe == "Unknown":
                utils.log_warning(f"Could not get process info for PID {pid}. Skipping connection.")
                continue
            else:
                try:
                    db.update_connection(
                            key = key,
                            name = name,
                            path = exe,
                            timestamp = utils.get_current_time(),
                            pid = pid,
                            local_port = local_port,
                            remote_ip = remote_ip,
                            remote_port = remote_port,
                            status = status
                    )
                    
                except Exception as e:
                    utils.log_error(f"Error updating database: {str(e)}")
                
                connection = db.convert_to_dict(db.get_connection(key)) if db.get_connection(key) else {}
                blacklisted = connection['blacklisted'] if connection != None else 0
                whitelisted = connection['whitelisted'] if connection != None else 0
                ignored_on = connection['ignored_on'] if connection else None

                utils.log_info(f"Connection: {name} {'blacklisted' if blacklisted else 'whitelisted' if whitelisted else 'unknown'}")
                
                if blacklisted and not whitelisted:
                    utils.log_info("  > Blacklisted connection detected!")

                if not whitelisted and not blacklisted:
                    if config["alerts"]["enabled"]:
                        triggers = config["alerts"]["triggers"]
                        trigger_limit = config["alerts"]["limit"] if config["alerts"]["trigger_limit"] else 0
                        trigger_count = 0

                        if triggers["external_ip"] and remote_ip != 0 and not is_private_ip(remote_ip):
                            utils.log_info("  > Trigger: External IP")
                            trigger_count += 1

                        if triggers["established_connection"] and status == "ESTABLISHED":
                            utils.log_info("  > Trigger: Established Connection")
                            trigger_count += 1

                        if triggers["missing_path"] and (exe == "Unknown" or not utils.file_exists(exe)):
                            utils.log_info("  > Trigger: Missing Executable Path")
                            trigger_count += 1

                        if triggers["from_downloads"] and "downloads" in exe.lower():
                            utils.log_info("  > Trigger: Executable from Downloads Folder")
                            trigger_count += 1

                        if triggers["unusual_port"] and remote_port not in [80, 443, 22, 21, 25, 110, 995]:
                            utils.log_info("  > Trigger: Unusual Remote Port")
                            trigger_count += 1

                        if trigger_limit and trigger_count < trigger_limit:
                            utils.log_info(f"  > Trigger count {trigger_count} below limit {trigger_limit}, not alerting.")
                        elif connection and ignored_on:
                            if utils.ignore_connection(ignored_on, 1): # Check if we should still ignore based on time (hours)
                                utils.log_debug("  > Connection is still within ignore period, skipping alert.")
                                continue
                        else:
                            utils.log_info("  > Alerting user about suspicious connection...")
                            
                            choice = await alerts.alert_user(
                                f"Suspicious connection detected**\n" +
                                f"Process: {name}\n" + f"PID: {pid}\n" +
                                f"Path: `{exe}`\n" +
                                f"Remote: `{f"{remote_ip}:{remote_port}"}`\n"
                            )
                            
                            
                            if choice == "Whitelist":
                                db.update_connection(key, blacklisted=0, whitelisted=1)
                            elif choice == "Blacklist":
                                db.update_connection(key, blacklisted=1, whitelisted=0)
                            elif choice == "Kill Once":
                                db.update_connection(key, blacklisted=0, whitelisted=0)
                                if pid != 0:
                                    kill_process(pid)
                            elif choice == "Ignore":
                                db.update_connection(key, blacklisted=0, whitelisted=0, ignored_on=utils.get_deltatime())
                                utils.log_info("  > User chose to ignore.")
                            else:
                                utils.log_info("  > No action taken.")
            
    except Exception as e:
        utils.log_error(f"Error scanning network: {str(e)}")