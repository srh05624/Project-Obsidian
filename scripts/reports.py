from scripts import installer, utils,db

def generate_report(db_path):
    try:
        connections = db.fetch_connections(db_path)
        report_lines = ["Name,Path,IP,Port,Local Port,PID,Status,Blacklisted,Whitelisted,Timestamp"]
        for conn in connections:
            line = f"{conn['name']},{conn['path']},{conn['remote_ip']},{conn['remote_port']},{conn['local_port']},{conn['pid']},{conn['status']},{conn['blacklisted']},{conn['whitelisted']},{conn['timestamp']}"
            report_lines.append(line)
        
        report_content = "\n".join(report_lines)
        report_path = installer.reports_path + "/network_report_" + utils.get_current_time().replace(":", "-") + ".csv"
        with open(report_path, "w") as f:
            f.write(report_content)
        
        response = {"success": True, "message": f"Report generated at {report_path}"}
        
    except Exception as e:
        utils.log_error(f"Error generating report: {str(e)}")
        response = {"success": False, "message": f"Error generating report: {str(e)}"}

    return response