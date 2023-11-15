# A Custom psutil library
import os
import sys
import stat
import pwd
import ctypes
import cshutil as shutil
import csubprocess as subprocess


def cls():
    """Clears the console."""
    if os.name == 'nt':  # If operating system is windows, use this code
        _ = os.system('cls')
    else:  # otherwise, use this code
        _ = os.system('clear')
def cpu_percent():
    """Returns information about the cpu"""
    if os.name == 'nt':
        obj = subprocess.popen('wmic path Win32_Processor get LoadPercentage', stdout=True)
        output = obj.stdout
    else:
        with open('/proc/stat') as stat_file:
            cpu_line = next(line for line in stat_file if line.startswith('cpu '))
            values = cpu_line.split()[1:]
            total_time = sum(map(int, values))
            idle_time = int(values[3])
            cpu_percentage = 100 * (1 - idle_time / total_time)
            output = f"{cpu_percentage:.2f}"
    return int(output.read().split('\n')[1])

def disk_usage(path):
    if os.name == 'nt':
        free_bytes = ctypes.c_ulonglong(0).value
        total_bytes = ctypes.c_ulonglong(0).value
        query = r'SELECT FreeSpace, TotalSize FROM win32_logicaldisk WHERE DeviceID="%s:"' % path
        try:
            wmi_obj = ctypes.CreateObject("winmgmts:{impersonationLevel=impersonate}").ExecQuery
            result = wmi_obj(query)[0]
            free_bytes = result.FreeSpace
            total_bytes = result.TotalSize
        except Exception as e:
            print(e)
        return {'total': total_bytes, 'used': total_bytes - free_bytes, 'free': free_bytes}
    else:
        st = os.statvfs(path)
        total, used, free = st.f_blocks * st.f_bsize, (st.f_blocks - st.f_bfree) * st.f_bsize, st.f_bfree * st.f_bsize
        return {'total': total, 'used': used, 'free': free}

def virtual_memory():
    """Returns information about system memory usage including total, available, used, and free memory."""
    memStats = {}
    if os.name == 'nt':  # Windows
        popenResult = subprocess.popen('systeminfo')
        out, err = popenResult.communicate()
        if not out:
            raise Exception("Failed to get memory stats")
        lines = out.split('\n')
        for line in lines:
            parts = line.strip().split(':', 2)
            if len(parts) == 3:
                key, value = parts[1], int(parts[2].replace(',', ''))
                if 'Total' in key:
                    memStats['total'] = value * 1024
                elif 'Available' in key:
                    memStats['available'] = value * 1024
                elif 'In use by applications' in key:
                    memStats['used'] = value * 1024
                else:
                    continue
        return memStats
    else:  # Unix-like systems
        with open('/proc/meminfo') as meminfo:
            for line in meminfo:
                parts = line.split(':')
                if len(parts) == 2:
                    key, value = parts[0].strip(), int(parts[1].split()[0]) * 1024
                    if 'MemTotal' in key:
                        memStats['total'] = value
                    elif 'MemFree' in key:
                        memStats['free'] = value
                    elif 'MemAvailable' in key:
                        memStats['available'] = value
                    elif 'Buffers' in key or 'Cached' in key:
                        memStats['used'] = memStats.get('used', 0) + value
        return memStats

def users():
    """List all logged-in user accounts on the current machine."""
    if os.name == 'nt':  # Windows
        try:
            result = subprocess.popen('net user')
            stdout, stderr = result.communicate()
            if stderr:
                print('Could not retrieve list of users')
                return []
        except Exception as e:
            print(f'Error: {e}')
            return []
        
        # Format the result
        users = []
        for line in stdout.split('\n'):
            if '@' in line or '#' in line:
                name = line.split('   ', 1)[0]
                domain = line.split('@', 1)[1].split('#', 1)[0]
                users.append((domain + '/' + name).rstrip())
        
        return users
    else:  # Unix-like systems
        try:
            result = subprocess.popen('who')
            stdout, stderr = result.communicate()
            if stderr:
                print('Could not retrieve list of users')
                return []
        except Exception as e:
            print(f'Error: {e}')
            return []
        
        # Format the result
        users = []
        for line in stdout.split('\n'):
            parts = line.strip().split()
            if len(parts) >= 1:
                users.append(parts[0])
        
        return users

def get_user():
    if os.name == 'nt':
        buf = ctypes.create_unicode_buffer(65536)
        ctypes.windll.secur32.GetUserNameExW(ctypes.c_int(1), buf, ctypes.pointer(ctypes.sizeof(buf)))
        return buf.value
    else:
        return pwd.getpwuid(os.geteuid()).pw_name
    
def get_user_session_info():
    if os.name == 'nt':
        try:
            result = subprocess.popen('query user')
            stdout, stderr = result.communicate()
            if stderr:
                print('Could not retrieve user session information on Windows')
                return []
        except Exception as e:
            print(f'Error: {e}')
            return []

        sessions = []
        lines = stdout.split('\n')
        for line in lines[2:]:  # Skip the first two lines as they are headers
            parts = line.strip().split()
            if len(parts) >= 3:
                username = parts[0]
                session_name = parts[1]
                session_id = parts[2]
                sessions.append({'username': username, 'session_name': session_name, 'session_id': session_id})

        return sessions
    else:
        try:
            result = subprocess.popen('who')
            stdout, stderr = result.communicate()
            if stderr:
                print('Could not retrieve user session information on Unix-like systems')
                return []
        except Exception as e:
            print(f'Error: {e}')
            return []

        sessions = []
        lines = stdout.split('\n')
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                username = parts[0]
                session_info = ' '.join(parts[1:])
                sessions.append({'username': username, 'session_info': session_info})

        return sessions