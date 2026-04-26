import os
import subprocess

def secure_read_file(filepath, current_user):
    """
    Allows both admin and user to read files.
    """
    if not os.path.exists(filepath):
        return {"status": "error", "message": "File not found"}
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return {"status": "success", "message": f"Read {len(content)} characters", "data": content}
    except Exception as e:
        return {"status": "error", "message": f"Error reading file: {str(e)}"}

def secure_write_file(filepath, content, current_user):
    """
    Allows only admin to write files.
    """
    if current_user.role != 'admin':
        return {"status": "denied", "message": "Permission denied: Only admin can write files"}
    
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return {"status": "success", "message": "File written successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error writing file: {str(e)}"}

def secure_delete_file(filepath, current_user):
    """
    Allows only admin to delete files.
    """
    if current_user.role != 'admin':
        return {"status": "denied", "message": "Permission denied: Only admin can delete files"}
    
    if not os.path.exists(filepath):
        return {"status": "error", "message": "File not found"}
    
    try:
        os.remove(filepath)
        return {"status": "success", "message": "File deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error deleting file: {str(e)}"}

def secure_execute_command(command, current_user):
    """
    Allows only admin to execute commands.
    """
    if current_user.role != 'admin':
        return {"status": "denied", "message": "Permission denied: Only admin can execute commands"}
    
    try:
        # Using subprocess.run for better security than os.system
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.returncode == 0 else result.stderr
        return {"status": "success" if result.returncode == 0 else "error", "message": f"Command executed with return code {result.returncode}", "data": output}
    except Exception as e:
        return {"status": "error", "message": f"Error executing command: {str(e)}"}
