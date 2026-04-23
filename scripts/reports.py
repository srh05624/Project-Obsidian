import csv
from scripts import installer, utils,db

def generate_report():
    try:
        connections = db.fetch_connections()
        print(f"Fetched {len(connections)} connections from database for report generation.")
        
        report_path = installer.reports_path + "/network_report_" + utils.get_current_time().replace(":", "-") + ".csv"
        with open(report_path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Key", "Name", "Path", "Remote IP", "Remote Port", "Local Port", "PID", "Status", "Blacklisted", "Whitelisted", "Timestamp"])
            for conn in connections:
                conn_dict = db.convert_to_dict(conn)
                if conn_dict:
                    writer.writerow([
                        conn_dict["key"],
                        conn_dict["name"],
                        conn_dict["path"],
                        conn_dict["remote_ip"],
                        conn_dict["remote_port"],
                        conn_dict["local_port"],
                        conn_dict["pid"],
                        conn_dict["status"],
                        "Yes" if conn_dict["blacklisted"] else "No",
                        "Yes" if conn_dict["whitelisted"] else "No",
                        conn_dict["timestamp"]
                    ])
        
        response = {"success": True, "message": f"Report generated at {report_path}"}
        
    except Exception as e:
        utils.log_error(f"Error generating report: {str(e)}")
        response = {"success": False, "message": f"Error generating report: {str(e)}"}

    return response