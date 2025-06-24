
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import hashlib
import uuid
import threading
import time
import platform
import subprocess
import re
import ctypes
import sys
import os
import atexit
import json

class WiFiDetector:
    """Enhanced WiFi BSSID detection with multiple fallback methods"""
    
    @staticmethod
    def get_current_bssid():
        """Get current WiFi BSSID using multiple detection methods"""
        methods = [
            WiFiDetector._netsh_method,
            WiFiDetector._powershell_method,
            WiFiDetector._wmic_method,
            WiFiDetector._netsh_profiles_method,
            WiFiDetector._ipconfig_method
        ]
        
        for method in methods:
            try:
                bssid = method()
                if bssid and WiFiDetector._is_valid_bssid(bssid):
                    print(f"BSSID detected using {method.__name__}: {bssid}")
                    return bssid
            except Exception as e:
                print(f"Method {method.__name__} failed: {e}")
                continue
        
        return None
    
    @staticmethod
    def _netsh_method():
        """Method 1: Using netsh wlan show interfaces"""
        cmd = 'netsh wlan show interfaces'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'BSSID' in line and ':' in line:
                    bssid = line.split(':', 1)[1].strip()
                    return WiFiDetector._standardize_bssid(bssid)
        return None
    
    @staticmethod
    def _powershell_method():
        """Method 2: Using PowerShell Get-NetAdapter"""
        cmd = '''powershell -command "
        $adapter = Get-NetAdapter | Where-Object {$_.MediaType -eq 'Native 802.11' -and $_.Status -eq 'Up'}
        if ($adapter) {
            $profile = netsh wlan show profiles | Select-String 'All User Profile' | ForEach-Object {$_.ToString().Split(':')[1].Trim()}
            if ($profile) {
                $details = netsh wlan show profile name=$profile[0] key=clear
                $bssid = $details | Select-String 'BSSID' | ForEach-Object {$_.ToString().Split(':')[1].Trim()}
                Write-Output $bssid
            }
        }"'''
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=15)
        if result.returncode == 0 and result.stdout.strip():
            return WiFiDetector._standardize_bssid(result.stdout.strip())
        return None
    
    @staticmethod
    def _wmic_method():
        """Method 3: Using WMIC for network adapters"""
        cmd = 'wmic path win32_networkadapter where "NetConnectionStatus=2 and AdapterTypeId=9" get MACAddress /value'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'MACAddress=' in line:
                    mac = line.split('=')[1].strip()
                    if mac:
                        return WiFiDetector._standardize_bssid(mac)
        return None
    
    @staticmethod
    def _netsh_profiles_method():
        """Method 4: Get BSSID from current connection profile"""
        # Get current connected profile
        cmd = 'netsh wlan show interfaces'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        
        profile_name = None
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'Profile' in line and ':' in line:
                    profile_name = line.split(':', 1)[1].strip()
                    break
        
        if profile_name:
            # Get profile details
            cmd = f'netsh wlan show profile name="{profile_name}" key=clear'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'BSSID' in line and ':' in line:
                        bssid = line.split(':', 1)[1].strip()
                        return WiFiDetector._standardize_bssid(bssid)
        return None
    
    @staticmethod
    def _ipconfig_method():
        """Method 5: Parse ipconfig /all for wireless adapter info"""
        cmd = 'ipconfig /all'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            in_wireless_section = False
            
            for i, line in enumerate(lines):
                if 'Wireless' in line and 'adapter' in line:
                    in_wireless_section = True
                elif line.strip() == '' and in_wireless_section:
                    in_wireless_section = False
                elif in_wireless_section and 'Physical Address' in line:
                    if ':' in line:
                        mac = line.split(':', 1)[1].strip()
                        return WiFiDetector._standardize_bssid(mac)
        return None
    
    @staticmethod
    def _standardize_bssid(raw_bssid):
        """Convert any MAC/BSSID format to standard aa:bb:cc:dd:ee:ff"""
        if not raw_bssid:
            return None
        
        # Remove all non-hex characters
        cleaned = re.sub(r'[^0-9A-Fa-f]', '', raw_bssid).lower()
        
        if len(cleaned) != 12:
            return None
        
        # Format as aa:bb:cc:dd:ee:ff
        return ':'.join(cleaned[i:i+2] for i in range(0, 12, 2))
    
    @staticmethod
    def _is_valid_bssid(bssid):
        """Validate BSSID format"""
        if not bssid:
            return False
        
        pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        return bool(re.match(pattern, bssid))

class StudentAuth:
    def __init__(self):
        self.server_url = "https://deadball-4ua9.onrender.com"
        self.current_student = None
        self.device_id = str(uuid.uuid4())
        self.classroom_bssid = None
        self.is_admin = self.check_admin_privileges()
        self.ping_thread = None
        self.running = True
        
        atexit.register(self.cleanup_on_exit)
    
    def cleanup_on_exit(self):
        """Clean up server state when program exits"""
        if self.current_student:
            try:
                requests.post(
                    f"{self.server_url}/student/cleanup_dead_sessions",
                    json={
                        'student_id': self.current_student['id'],
                        'device_id': self.device_id
                    },
                    timeout=5
                )
            except:
                pass
    
    def check_admin_privileges(self):
        """Check if running with admin privileges"""
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            return True
        except:
            return False
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_current_bssid(self):
        """Get current WiFi BSSID"""
        return WiFiDetector.get_current_bssid()
    
    def student_login(self, student_id, password):
        
        try:
            # Step 1: Login student
            response = requests.post(
                f"{self.server_url}/student/login",
                json={
                    'id': student_id,
                    'password': self.hash_password(password),
                    'device_id': self.device_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_student = data['student']

                # Step 2: Try fetching expected BSSID by calling teacher login
                try:
                    teacher_login = requests.post(
                        f"{self.server_url}/teacher/login",
                        json={
                            'id': 'admin',         # Replace with any safe teacher ID
                            'password': 'admin'    # Replace with corresponding password
                        },
                        timeout=5
                    )
                    
                    if teacher_login.status_code == 200:
                        teacher_data = teacher_login.json().get('teacher')
                        bssid_map = teacher_data.get('bssid_mapping', {})
                        classroom = self.current_student['classroom']
                        self.classroom_bssid = bssid_map.get(classroom)
                        print(f"Expected BSSID for classroom {classroom}: {self.classroom_bssid}")
                    else:
                        print("Warning: Teacher login failed while fetching BSSID mapping")
                        self.classroom_bssid = None
                
                except Exception as e:
                    print(f"Error during BSSID mapping fetch: {e}")
                    self.classroom_bssid = None

                return True, "Login successful"

            return False, response.json().get('error', 'Login failed')

        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

        
    def check_in(self, bssid=None):
        try:
            response = requests.post(
                f"{self.server_url}/student/checkin",
                json={
                    'student_id': self.current_student['id'],
                    'bssid': bssid,
                    'device_id': self.device_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data['message'], data.get('status')
            return False, response.json().get('error', 'Check-in failed'), None
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}", None
    
    def start_timer(self):
        try:
            response = requests.post(
                f"{self.server_url}/student/timer/start",
                json={
                    'student_id': self.current_student['id'],
                    'device_id': self.device_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()['message']
            return False, response.json().get('error', 'Failed to start timer')
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def stop_timer(self):
        try:
            response = requests.post(
                f"{self.server_url}/student/timer/stop",
                json={
                    'student_id': self.current_student['id'],
                    'device_id': self.device_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()['message']
            return False, response.json().get('error', 'Failed to stop timer')
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def get_status(self):
        try:
            response = requests.get(
                f"{self.server_url}/student/get_status",
                params={
                    'student_id': self.current_student['id'],
                    'device_id': self.device_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            return False, response.json().get('error', 'Failed to get status')
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def get_attendance(self):
        try:
            response = requests.get(
                f"{self.server_url}/student/get_attendance",
                params={
                    'student_id': self.current_student['id'],
                    'device_id': self.device_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()['attendance']
            return False, response.json().get('error', 'Failed to get attendance')
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def get_timetable(self):
        try:
            response = requests.get(
                f"{self.server_url}/student/get_timetable",
                params={
                    'student_id': self.current_student['id'],
                    'branch': self.current_student['branch'],
                    'semester': self.current_student['semester']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()['timetable']
            return False, response.json().get('error', 'Failed to get timetable')
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def send_ping(self):
        try:
            response = requests.post(
                f"{self.server_url}/student/ping",
                json={
                    'student_id': self.current_student['id'],
                    'device_id': self.device_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()['message']
            return False, response.json().get('error', 'Ping failed')
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

class LoginWindow:
    def __init__(self, auth_system):
        self.auth = auth_system
        self.root = tk.Tk()
        self.root.title("Student Attendance Login")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Student Attendance System", 
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(pady=(0, 30))
        
        # Login form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Student ID
        ttk.Label(form_frame, text="Student ID:", font=('Segoe UI', 11)).pack(anchor='w', pady=(0, 5))
        self.student_id = ttk.Entry(form_frame, font=('Segoe UI', 11))
        self.student_id.pack(fill=tk.X, pady=(0, 15))
        
        # Password
        ttk.Label(form_frame, text="Password:", font=('Segoe UI', 11)).pack(anchor='w', pady=(0, 5))
        self.password = ttk.Entry(form_frame, show="●", font=('Segoe UI', 11))
        self.password.pack(fill=tk.X, pady=(0, 25))
        
        # Login button
        login_btn = ttk.Button(
            form_frame, 
            text="Login", 
            command=self.login,
            style='Accent.TButton'
        )
        login_btn.pack(fill=tk.X, pady=(0, 15))
        
        # WiFi Test button
        test_btn = ttk.Button(
            form_frame, 
            text="Test WiFi Detection", 
            command=self.test_wifi
        )
        test_btn.pack(fill=tk.X)
        
        # Status info
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Admin status
        admin_status = "✓ Administrator" if self.auth.is_admin else "⚠ Standard User"
        admin_color = "green" if self.auth.is_admin else "orange"
        ttk.Label(
            status_frame, 
            text=f"Privileges: {admin_status}", 
            foreground=admin_color
        ).pack(anchor='w')
        
        # Platform info
        ttk.Label(
            status_frame, 
            text=f"Platform: {platform.system()} {platform.release()}"
        ).pack(anchor='w')
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
        self.student_id.focus()
    
    def test_wifi(self):
        """Test WiFi BSSID detection"""
        self.root.config(cursor="watch")
        self.root.update()
        
        bssid = self.auth.get_current_bssid()
        
        self.root.config(cursor="")
        
        if bssid:
            messagebox.showinfo(
                "WiFi Detection Test", 
                f"✓ BSSID detected successfully!\n\nCurrent BSSID: {bssid}\n\nYour WiFi detection is working properly."
            )
        else:
            messagebox.showwarning(
                "WiFi Detection Test", 
                "⚠ Could not detect WiFi BSSID.\n\nTroubleshooting:\n"
                "1. Ensure you're connected to WiFi\n"
                "2. Try running as Administrator\n"
                "3. Check if your WiFi adapter is working\n"
                "4. Contact IT support if issues persist"
            )
    
    def login(self):
        student_id = self.student_id.get().strip()
        password = self.password.get()
        
        if not student_id or not password:
            messagebox.showwarning("Input Error", "Please enter both Student ID and Password")
            return
        
        self.root.config(cursor="watch")
        self.root.update()
        
        success, message = self.auth.student_login(student_id, password)
        
        self.root.config(cursor="")
        
        if success:
            self.root.destroy()
            StudentDashboard(self.auth).run()
        else:
            messagebox.showerror("Login Failed", message)
    
    def run(self):
        self.root.mainloop()

class StudentDashboard:
    def __init__(self, auth_system):
        self.auth = auth_system
        self.current_status = None
        self.timer_running = False
        self.auto_refresh_active = True
        
        self.root = tk.Tk()
        self.root.title(f"Dashboard - {self.auth.current_student['name']}")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)
        
        self.setup_ui()
        self.update_status()
        self.auto_refresh()
        self.start_ping_thread()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        """Handle window close event"""
        self.auto_refresh_active = False
        self.auth.running = False
        if self.auth.ping_thread and self.auth.ping_thread.is_alive():
            self.auth.ping_thread.join(timeout=1)
        self.root.destroy()
    
    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame, 
            text=f"Welcome, {self.auth.current_student['name']}", 
            font=('Segoe UI', 16, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            header_frame, 
            text="Refresh", 
            command=self.update_status
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            header_frame, 
            text="Test WiFi", 
            command=self.test_wifi_detection
        ).pack(side=tk.RIGHT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_container, text="Current Status", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Student info grid
        info_grid = ttk.Frame(status_frame)
        info_grid.pack(fill=tk.X, pady=(0, 15))
        
        # Configure grid columns
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
        
        # Row 0
        ttk.Label(info_grid, text="Student ID:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='e', padx=(0, 10))
        ttk.Label(info_grid, text=self.auth.current_student['id']).grid(row=0, column=1, sticky='w')
        
        ttk.Label(info_grid, text="Classroom:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, sticky='e', padx=(20, 10))
        ttk.Label(info_grid, text=self.auth.current_student['classroom']).grid(row=0, column=3, sticky='w')
        
        # Row 1
        ttk.Label(info_grid, text="Branch:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=(0, 10), pady=(5, 0))
        ttk.Label(info_grid, text=self.auth.current_student['branch']).grid(row=1, column=1, sticky='w', pady=(5, 0))
        
        ttk.Label(info_grid, text="Semester:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=2, sticky='e', padx=(20, 10), pady=(5, 0))
        ttk.Label(info_grid, text=self.auth.current_student['semester']).grid(row=1, column=3, sticky='w', pady=(5, 0))
        
        # Connection status
        conn_frame = ttk.LabelFrame(status_frame, text="Connection Status", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 15))
        
        conn_grid = ttk.Frame(conn_frame)
        conn_grid.pack(fill=tk.X)
        conn_grid.columnconfigure(1, weight=1)
        
        ttk.Label(conn_grid, text="Server:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='e', padx=(0, 10))
        self.conn_status = ttk.Label(conn_grid, text="Checking...")
        self.conn_status.grid(row=0, column=1, sticky='w')
        
        ttk.Label(conn_grid, text="WiFi Status:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=(0, 10), pady=(5, 0))
        self.wifi_status = ttk.Label(conn_grid, text="Checking...")
        self.wifi_status.grid(row=1, column=1, sticky='w', pady=(5, 0))
        
        ttk.Label(conn_grid, text="Expected BSSID:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='e', padx=(0, 10), pady=(5, 0))
        self.expected_bssid_label = ttk.Label(conn_grid, text=self.auth.classroom_bssid or "Not set")
        self.expected_bssid_label.grid(row=2, column=1, sticky='w', pady=(5, 0))
        
        ttk.Label(conn_grid, text="Current BSSID:", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky='e', padx=(0, 10), pady=(5, 0))
        self.current_bssid_label = ttk.Label(conn_grid, text="Detecting...")
        self.current_bssid_label.grid(row=3, column=1, sticky='w', pady=(5, 0))
        
        # Timer status
        timer_frame = ttk.LabelFrame(status_frame, text="Timer Status", padding=10)
        timer_frame.pack(fill=tk.X, pady=(0, 15))
        
        timer_grid = ttk.Frame(timer_frame)
        timer_grid.pack(fill=tk.X)
        timer_grid.columnconfigure(1, weight=1)
        
        ttk.Label(timer_grid, text="Status:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='e', padx=(0, 10))
        self.timer_status_label = ttk.Label(timer_grid, text="Not running")
        self.timer_status_label.grid(row=0, column=1, sticky='w')
        
        ttk.Label(timer_grid, text="Time Remaining:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=(0, 10), pady=(5, 0))
        self.time_remaining_label = ttk.Label(timer_grid, text="00:00")
        self.time_remaining_label.grid(row=1, column=1, sticky='w', pady=(5, 0))
        
        # Action buttons
        btn_frame = ttk.Frame(status_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.checkin_btn = ttk.Button(
            btn_frame, 
            text="Check In", 
            command=self.check_in,
            style='Accent.TButton'
        )
        self.checkin_btn.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.start_timer_btn = ttk.Button(
            btn_frame, 
            text="Start Timer", 
            command=self.start_timer
        )
        self.start_timer_btn.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.stop_timer_btn = ttk.Button(
            btn_frame, 
            text="Stop Timer", 
            command=self.stop_timer
        )
        self.stop_timer_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Attendance tab
        attendance_frame = ttk.Frame(notebook)
        notebook.add(attendance_frame, text="Attendance History")
        
        self.attendance_tree = ttk.Treeview(
            attendance_frame,
            columns=("date", "subject", "status", "time"),
            show="headings",
            selectmode="browse"
        )
        
        self.attendance_tree.heading("date", text="Date")
        self.attendance_tree.heading("subject", text="Subject")
        self.attendance_tree.heading("status", text="Status")
        self.attendance_tree.heading("time", text="Time")
        
        self.attendance_tree.column("date", width=120)
        self.attendance_tree.column("subject", width=200)
        self.attendance_tree.column("status", width=100)
        self.attendance_tree.column("time", width=200)
        
        scrollbar1 = ttk.Scrollbar(attendance_frame, orient="vertical", command=self.attendance_tree.yview)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        self.attendance_tree.configure(yscrollcommand=scrollbar1.set)
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        
        # Timetable tab
        timetable_frame = ttk.Frame(notebook)
        notebook.add(timetable_frame, text="Timetable")
        
        self.timetable_tree = ttk.Treeview(
            timetable_frame,
            columns=("day", "start", "end", "subject", "room"),
            show="headings",
            selectmode="browse"
        )
        
        self.timetable_tree.heading("day", text="Day")
        self.timetable_tree.heading("start", text="Start Time")
        self.timetable_tree.heading("end", text="End Time")
        self.timetable_tree.heading("subject", text="Subject")
        self.timetable_tree.heading("room", text="Room")
        
        self.timetable_tree.column("day", width=100)
        self.timetable_tree.column("start", width=100)
        self.timetable_tree.column("end", width=100)
        self.timetable_tree.column("subject", width=200)
        self.timetable_tree.column("room", width=100)
        
        scrollbar2 = ttk.Scrollbar(timetable_frame, orient="vertical", command=self.timetable_tree.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.timetable_tree.configure(yscrollcommand=scrollbar2.set)
        self.timetable_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load initial data
        self.load_attendance_data()
        self.load_timetable_data()
    
    def test_wifi_detection(self):
        """Test WiFi BSSID detection and show detailed results"""
        self.root.config(cursor="watch")
        self.root.update()
        
        current_bssid = self.auth.get_current_bssid()
        expected_bssid = self.auth.classroom_bssid
        
        self.root.config(cursor="")
        
        if current_bssid:
            if expected_bssid and current_bssid == expected_bssid:
                status = "✓ Perfect Match!"
                color = "green"
                message = f"Your WiFi BSSID matches the classroom requirement perfectly.\n\nCurrent: {current_bssid}\nExpected: {expected_bssid}\n\nYou can proceed with check-in."
            elif expected_bssid:
                status = "⚠ Different Network"
                color = "orange"
                message = f"You're connected to a different WiFi network.\n\nCurrent: {current_bssid}\nExpected: {expected_bssid}\n\nPlease connect to the correct classroom WiFi."
            else:
                status = "✓ Detection Working"
                color = "blue"
                message = f"WiFi BSSID detection is working correctly.\n\nCurrent BSSID: {current_bssid}\n\nNo expected BSSID set by teacher yet."
        else:
            status = "✗ Detection Failed"
            color = "red"
            message = "Could not detect WiFi BSSID.\n\nPossible solutions:\n• Run as Administrator\n• Check WiFi connection\n• Contact IT support"
        
        # Update the display
        self.current_bssid_label.config(text=current_bssid or "Not detected", foreground=color)
        
        messagebox.showinfo("WiFi Detection Test", f"{status}\n\n{message}")
    
    def check_in(self):
        current_bssid = self.auth.get_current_bssid()
        
        if current_bssid is None:
            messagebox.showwarning(
                "WiFi Detection Failed",
                "Could not detect your WiFi BSSID.\n\nPlease:\n"
                "1. Ensure you're connected to WiFi\n"
                "2. Try running as Administrator\n"
                "3. Test WiFi detection first\n"
                "4. Contact support if issues persist"
            )
            return
        
        self.root.config(cursor="watch")
        self.root.update()
        
        success, message, status = self.auth.check_in(bssid=current_bssid)
        
        self.root.config(cursor="")
        
        if success:
            messagebox.showinfo("Check-In Successful", f"Status: {status}\n\n{message}")
            self.update_status()
        else:
            messagebox.showerror("Check-In Failed", message)
    
    def start_timer(self):
        self.root.config(cursor="watch")
        self.root.update()
        
        success, message = self.auth.start_timer()
        
        self.root.config(cursor="")
        
        if success:
            messagebox.showinfo("Timer Started", message)
            self.timer_running = True
            self.update_status()
        else:
            messagebox.showerror("Timer Error", message)
    
    def stop_timer(self):
        self.root.config(cursor="watch")
        self.root.update()
        
        success, message = self.auth.stop_timer()
        
        self.root.config(cursor="")
        
        if success:
            messagebox.showinfo("Timer Stopped", message)
            self.timer_running = False
            self.update_status()
        else:
            messagebox.showerror("Timer Error", message)
    
    def update_status(self):
        self.root.config(cursor="watch")
        self.root.update()
        
        success, status_data = self.auth.get_status()
        
        self.root.config(cursor="")
        
        if success:
            self.current_status = status_data
            self.update_status_display()
        else:
            self.conn_status.config(text="Connection failed", foreground="red")
    
    def update_status_display(self):
        if not self.current_status:
            return
        
        # Server connection status
        conn_status = self.current_status.get('connected', False)
        self.conn_status.config(
            text="Connected" if conn_status else "Disconnected",
            foreground="green" if conn_status else "red"
        )
        
        # WiFi status
        current_bssid = self.auth.get_current_bssid()
        expected_bssid = self.current_status.get('expected_bssid', self.auth.classroom_bssid)
        
        self.current_bssid_label.config(text=current_bssid or "Not detected")
        self.expected_bssid_label.config(text=expected_bssid or "Not set")
        
        if not current_bssid:
            wifi_text = "BSSID not detected"
            wifi_color = "red"
        elif expected_bssid and current_bssid == expected_bssid:
            wifi_text = "✓ Correct classroom WiFi"
            wifi_color = "green"
        elif expected_bssid:
            wifi_text = "⚠ Wrong WiFi network"
            wifi_color = "orange"
        else:
            wifi_text = "WiFi detected (no requirement set)"
            wifi_color = "blue"
        
        self.wifi_status.config(text=wifi_text, foreground=wifi_color)
        
        # Timer status
        timer = self.current_status.get('timer', {})
        if timer.get('status') == 'running':
            self.timer_status_label.config(text="Running", foreground="green")
            remaining = int(timer.get('remaining', 0))
            mins, secs = divmod(remaining, 60)
            self.time_remaining_label.config(text=f"{mins:02d}:{secs:02d}", foreground="green")
            
            self.start_timer_btn.config(state='disabled')
            self.stop_timer_btn.config(state='normal')
        else:
            self.timer_status_label.config(text="Not running", foreground="gray")
            self.time_remaining_label.config(text="00:00", foreground="gray")
            
            self.start_timer_btn.config(state='normal')
            self.stop_timer_btn.config(state='disabled')
    
    def load_attendance_data(self):
        success, attendance_data = self.auth.get_attendance()
        
        if success:
            for item in self.attendance_tree.get_children():
                self.attendance_tree.delete(item)
            
            for date, sessions in attendance_data.items():
                for session_id, session in sessions.items():
                    self.attendance_tree.insert("", "end", values=(
                        date,
                        session.get('subject', 'N/A'),
                        session.get('status', 'N/A'),
                        f"{session.get('start_time', '')} - {session.get('end_time', '')}"
                    ))
    
    def load_timetable_data(self):
        success, timetable_data = self.auth.get_timetable()
        
        if success:
            for item in self.timetable_tree.get_children():
                self.timetable_tree.delete(item)
            
            for slot in timetable_data:
                self.timetable_tree.insert("", "end", values=slot)
    
    def auto_refresh(self):
        if self.auto_refresh_active:
            self.update_status()
            self.root.after(10000, self.auto_refresh)  # Refresh every 10 seconds
    
    def start_ping_thread(self):
        def ping_loop():
            while self.auth.running:
                try:
                    self.auth.send_ping()
                except:
                    pass
                time.sleep(30)  # Ping every 30 seconds
        
        self.auth.ping_thread = threading.Thread(target=ping_loop, daemon=True)
        self.auth.ping_thread.start()
    
    def run(self):
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        self.root.mainloop()

def main():
    """Main application entry point"""
    try:
        print("Starting Student Attendance System...")
        print(f"Platform: {platform.system()} {platform.release()}")
        
        # Create authentication system
        auth_system = StudentAuth()
        
        print(f"Admin privileges: {'Yes' if auth_system.is_admin else 'No'}")
        print(f"Device ID: {auth_system.device_id}")
        
        # Test WiFi detection on startup
        print("Testing WiFi detection...")
        test_bssid = auth_system.get_current_bssid()
        if test_bssid:
            print(f"WiFi BSSID detected: {test_bssid}")
        else:
            print("Warning: Could not detect WiFi BSSID")
        
        # Start the application
        LoginWindow(auth_system).run()
        
    except Exception as e:
        error_msg = f"Fatal error occurred:\n\n{str(e)}\n\nPlease contact support."
        print(f"Error: {e}")
        
        try:
            messagebox.showerror("Application Error", error_msg)
        except:
            print(error_msg)
        
        sys.exit(1)

if __name__ == "__main__":
    main()
