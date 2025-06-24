import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import random
from datetime import datetime, time, timedelta
import hashlib
import uuid
from tkinter import font as tkfont

class TeacherAuth:
    def __init__(self):
        self.server_url = "https://deadball-4ua9.onrender.com"  # Update with your server URL
        self.current_teacher = None
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def teacher_signup(self, teacher_id, password, email, name):
        """Register a new teacher"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/signup",
                json={
                    'id': teacher_id,
                    'password': password,
                    'email': email,
                    'name': name
                }
            )
            
            if response.status_code == 201:
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'Registration failed')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def teacher_login(self, teacher_id, password):
        """Authenticate teacher"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/login",
                json={
                    'id': teacher_id,
                    'password': password
                }
            )
            
            if response.status_code == 200:
                self.current_teacher = response.json()['teacher']
                return True, "Login successful"
            else:
                return False, response.json().get('error', 'Login failed')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"

    def register_student(self, student_id, password, name, classroom, branch, semester):
        """Register a new student"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/register_student",
                json={
                    'id': student_id,
                    'password': self.hash_password(password),  # Hash before sending
                    'name': name,
                    'classroom': classroom,
                    'branch': branch,
                    'semester': semester
                }
            )
            
            if response.status_code == 201:
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'Registration failed')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def get_students(self, classroom=None, branch=None, semester=None):
        """Get list of students with optional filters"""
        try:
            params = {}
            if classroom:
                params['classroom'] = classroom
            if branch:
                params['branch'] = branch
            if semester:
                params['semester'] = semester
                
            response = requests.get(
                f"{self.server_url}/teacher/get_students",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()['students']
            else:
                print(f"Error getting students: {response.json().get('error')}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error getting students: {e}")
            return []
    
    def update_student(self, student_id, new_data):
        """Update student information"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/update_student",
                json={
                    'id': student_id,
                    'new_data': new_data
                }
            )
            
            if response.status_code == 200:
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'Update failed')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def delete_student(self, student_id):
        """Delete a student"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/delete_student",
                json={
                    'id': student_id
                }
            )
            
            if response.status_code == 200:
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'Deletion failed')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def update_teacher_profile(self, teacher_id, new_data):
        """Update teacher profile information"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/update_profile",
                json={
                    'id': teacher_id,
                    'new_data': new_data
                }
            )
            
            if response.status_code == 200:
                # Update current teacher if it's the same
                if self.current_teacher and self.current_teacher['id'] == teacher_id:
                    self.current_teacher.update(new_data)
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'Update failed')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def change_teacher_password(self, teacher_id, old_password, new_password):
        """Change teacher password"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/change_password",
                json={
                    'id': teacher_id,
                    'old_password': old_password,
                    'new_password': new_password
                }
            )
            
            if response.status_code == 200:
                # Update current teacher if it's the same
                if self.current_teacher and self.current_teacher['id'] == teacher_id:
                    self.current_teacher['password'] = self.hash_password(new_password)
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'Password change failed')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def update_bssid_mapping(self, teacher_id, classroom, bssid):
        """Update BSSID mapping for a classroom"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/update_bssid",
                json={
                    'teacher_id': teacher_id,
                    'classroom': classroom,
                    'bssid': bssid
                }
            )
            
            if response.status_code == 200:
                # Update current teacher if it's the same
                if self.current_teacher and self.current_teacher['id'] == teacher_id:
                    if 'bssid_mapping' not in self.current_teacher:
                        self.current_teacher['bssid_mapping'] = {}
                    self.current_teacher['bssid_mapping'][classroom] = bssid
                    
                    if classroom not in self.current_teacher['classrooms']:
                        self.current_teacher['classrooms'].append(classroom)
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'BSSID update failed')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def get_timetable(self, branch, semester):
        """Get timetable for branch and semester"""
        try:
            response = requests.get(
                f"{self.server_url}/teacher/get_timetable",
                params={
                    'branch': branch,
                    'semester': semester
                }
            )
            
            if response.status_code == 200:
                return True, response.json()['timetable']
            else:
                return False, response.json().get('error', 'Failed to get timetable')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def update_timetable(self, branch, semester, timetable):
        """Update timetable for branch and semester"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/update_timetable",
                json={
                    'branch': branch,
                    'semester': semester,
                    'timetable': timetable
                }
            )
            
            if response.status_code == 200:
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'Failed to update timetable')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def get_special_dates(self):
        """Get special dates (holidays and special schedules)"""
        try:
            response = requests.get(
                f"{self.server_url}/teacher/get_special_dates"
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json().get('error', 'Failed to get special dates')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"
    
    def update_special_dates(self, holidays, special_dates):
        """Update special dates (holidays and special schedules)"""
        try:
            response = requests.post(
                f"{self.server_url}/teacher/update_special_dates",
                json={
                    'holidays': holidays,
                    'special_dates': special_dates
                }
            )
            
            if response.status_code == 200:
                return True, response.json()['message']
            else:
                return False, response.json().get('error', 'Failed to update special dates')
        except requests.exceptions.RequestException:
            return False, "Could not connect to server"

class LoginWindow:
    def __init__(self, auth_system):
        self.auth = auth_system
        self.root = tk.Tk()
        self.root.title("Teacher Login")
        self.root.geometry("400x300")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Notebook for login/signup tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Login Frame
        login_frame = tk.Frame(self.notebook)
        self.notebook.add(login_frame, text="Login")
        
        tk.Label(login_frame, text="Teacher ID:").pack(pady=(20, 5))
        self.login_id = tk.Entry(login_frame)
        self.login_id.pack(pady=5)
        
        tk.Label(login_frame, text="Password:").pack(pady=5)
        self.login_password = tk.Entry(login_frame, show="*")
        self.login_password.pack(pady=5)
        
        tk.Button(login_frame, text="Login", command=self.login).pack(pady=20)
        
        # Signup Frame
        signup_frame = tk.Frame(self.notebook)
        self.notebook.add(signup_frame, text="Sign Up")
        
        tk.Label(signup_frame, text="Teacher ID:").pack(pady=(20, 5))
        self.signup_id = tk.Entry(signup_frame)
        self.signup_id.pack(pady=5)
        
        tk.Label(signup_frame, text="Password:").pack(pady=5)
        self.signup_password = tk.Entry(signup_frame, show="*")
        self.signup_password.pack(pady=5)
        
        tk.Label(signup_frame, text="Email:").pack(pady=5)
        self.signup_email = tk.Entry(signup_frame)
        self.signup_email.pack(pady=5)
        
        tk.Label(signup_frame, text="Full Name:").pack(pady=5)
        self.signup_name = tk.Entry(signup_frame)
        self.signup_name.pack(pady=5)
        
        tk.Button(signup_frame, text="Register", command=self.signup).pack(pady=20)
    
    def login(self):
        teacher_id = self.login_id.get()
        password = self.login_password.get()
        
        if not teacher_id or not password:
            messagebox.showwarning("Warning", "Please enter both ID and password")
            return
        
        success, message = self.auth.teacher_login(teacher_id, password)
        if success:
            self.root.destroy()
            TeacherDashboard(self.auth).run()
        else:
            messagebox.showerror("Error", message)
    
    def signup(self):
        teacher_id = self.signup_id.get()
        password = self.signup_password.get()
        email = self.signup_email.get()
        name = self.signup_name.get()
        
        if not all([teacher_id, password, email, name]):
            messagebox.showwarning("Warning", "Please fill all fields")
            return
        
        success, message = self.auth.teacher_signup(teacher_id, password, email, name)
        if success:
            messagebox.showinfo("Success", message)
            self.notebook.select(0)  # Switch to login tab
        else:
            messagebox.showerror("Error", message)
    
    def run(self):
        self.root.mainloop()

class TeacherDashboard:
    def __init__(self, auth_system):
        self.auth = auth_system
        self.server_url = self.auth.server_url
        self.student_attendance = {}  # To track attendance history
        self.current_session = None  # To track current session
        self.manual_overrides = {}  # Track manual attendance overrides
        self.current_classroom = None
        self.current_branch = None
        self.current_semester = None
        self.reminder_shown = False
        self.special_dates = {"holidays": [], "special_schedules": []}
        self.timetable_data = {"default": []}
        
        # Load initial data
        self.load_initial_data()
        
        self.root = tk.Tk()
        self.root.title(f"Teacher Dashboard - {self.auth.current_teacher['name']}")
        self.root.geometry("1400x800")
        
        # Menu Bar
        self.setup_menu()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for each tab
        self.dashboard_frame = tk.Frame(self.notebook)
        self.timetable_frame = tk.Frame(self.notebook)
        self.students_frame = tk.Frame(self.notebook)
        self.reports_frame = tk.Frame(self.notebook)
        self.settings_frame = tk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.timetable_frame, text="Timetable")
        self.notebook.add(self.students_frame, text="Students")
        self.notebook.add(self.reports_frame, text="Reports")
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Dashboard Tab
        self.setup_dashboard_tab()
        
        # Timetable Tab
        self.setup_timetable_tab()
        
        # Students Tab
        self.setup_students_tab()
        
        # Reports Tab
        self.setup_reports_tab()
        
        # Settings Tab
        self.setup_settings_tab()
        
        # Status label (Bottom)
        teacher_info = self.auth.current_teacher
        self.status_label = tk.Label(
            self.root, 
            text=f"Teacher: {teacher_info['name']} ({teacher_info['id']}) | Classroom: {self.current_classroom or 'Not selected'} | Branch/Semester: {self.current_branch or 'None'}/{self.current_semester or 'None'} | Session: Not active", 
            fg="blue"
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Auto-refresh every 2 seconds
        self.update_dashboard()
        self.auto_refresh()
        
        # Show random ring reminder if not shown yet
        if not self.reminder_shown:
            self.show_random_ring_reminder()
    
    def load_initial_data(self):
        """Load initial data from server"""
        # Load special dates
        success, data = self.auth.get_special_dates()
        if success:
            self.special_dates = data
    
    def manage_sessions(self):
        """Show a window to manage active sessions"""
        try:
            response = requests.get(
                f"{self.server_url}/teacher/get_active_sessions",
                params={'teacher_id': self.auth.current_teacher['id']}
            )
            
            if response.status_code == 200:
                sessions = response.json().get('sessions', [])
                
                # Create the sessions window
                sessions_window = tk.Toplevel(self.root)
                sessions_window.title("Manage Active Sessions")
                sessions_window.geometry("800x400")
                
                # Treeview to display sessions
                tree = ttk.Treeview(sessions_window, columns=("id", "subject", "classroom", "branch", "semester", "start_time"), show="headings")
                tree.heading("id", text="Session ID")
                tree.heading("subject", text="Subject")
                tree.heading("classroom", text="Classroom")
                tree.heading("branch", text="Branch")
                tree.heading("semester", text="Semester")
                tree.heading("start_time", text="Start Time")
                
                tree.column("id", width=100)
                tree.column("subject", width=150)
                tree.column("classroom", width=100)
                tree.column("branch", width=80)
                tree.column("semester", width=80)
                tree.column("start_time", width=150)
                
                tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Add sessions to treeview
                for session in sessions:
                    tree.insert("", "end", values=(
                        session['id'],
                        session['subject'],
                        session['classroom'],
                        session.get('branch', 'N/A'),
                        session.get('semester', 'N/A'),
                        session['start_time']
                    ))
                
                # End Session button
                def end_selected_session():
                    selected = tree.selection()
                    if not selected:
                        messagebox.showwarning("Warning", "Please select a session to end")
                        return
                    
                    session_id = tree.item(selected[0], 'values')[0]
                    
                    try:
                        response = requests.post(
                            f"{self.server_url}/teacher/end_session",
                            json={'session_id': session_id}
                        )
                        
                        if response.status_code == 200:
                            messagebox.showinfo("Success", "Session ended successfully")
                            sessions_window.destroy()
                            self.update_dashboard()
                        else:
                            messagebox.showerror("Error", response.json().get('error', 'Failed to end session'))
                    except requests.exceptions.RequestException:
                        messagebox.showerror("Error", "Could not connect to server")
                
                tk.Button(sessions_window, text="End Selected Session", command=end_selected_session).pack(pady=10)
                
            else:
                messagebox.showerror("Error", response.json().get('error', 'Failed to get sessions'))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")

    def show_random_ring_reminder(self):
        """Show reminder about random ring feature"""
        self.reminder_shown = True
        reminder = tk.Toplevel(self.root)
        reminder.title("Reminder")
        reminder.geometry("400x200")
        
        # Make the window stay on top
        reminder.attributes('-topmost', True)
        reminder.after(100, lambda: reminder.attributes('-topmost', False))
        
        # Bold title
        title_font = tkfont.Font(size=12, weight='bold')
        tk.Label(reminder, text="Random Ring Reminder", font=title_font).pack(pady=10)
        
        # Message
        message = "Remember to use the Random Ring feature during your class sessions!\n\n"
        message += "This feature helps engage students with different attendance patterns."
        tk.Label(reminder, text=message, wraplength=350).pack(pady=10)
        
        # OK button
        tk.Button(reminder, text="OK", command=reminder.destroy).pack(pady=10)
        
        # Fade out after 10 seconds if not closed
        reminder.after(10000, self.fade_out, reminder)
    
    def fade_out(self, window):
        """Gradually fade out the window"""
        alpha = window.attributes('-alpha')
        if alpha > 0.1:
            alpha -= 0.1
            window.attributes('-alpha', alpha)
            window.after(100, self.fade_out, window)
        else:
            window.destroy()
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Actions menu
        action_menu = tk.Menu(menubar, tearoff=0)
        action_menu.add_command(label="Register Student", command=self.show_student_registration)
        action_menu.add_command(label="Change Classroom", command=self.select_classroom)
        action_menu.add_command(label="Change Branch/Semester", command=self.select_branch_semester)
        menubar.add_cascade(label="Actions", menu=action_menu)
        
        self.root.config(menu=menubar)
    
    def setup_dashboard_tab(self):
        # Main container frames
        top_frame = tk.Frame(self.dashboard_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        middle_frame = tk.Frame(self.dashboard_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Control Frame (Top)
        control_frame = tk.Frame(top_frame)
        control_frame.pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="Manage Sessions", command=self.manage_sessions).pack(side=tk.LEFT, padx=5)
        
        # BSSID Control
        bssid_frame = tk.Frame(control_frame)
        bssid_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(bssid_frame, text="Authorized BSSID:").pack(side=tk.LEFT)
        self.bssid_entry = tk.Entry(bssid_frame, width=20)
        self.bssid_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(bssid_frame, text="Set BSSID", command=self.set_bssid).pack(side=tk.LEFT)
        
        # Session Controls (Top Right)
        session_frame = tk.Frame(top_frame)
        session_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(session_frame, text="Start Session", command=self.start_session, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        tk.Button(session_frame, text="End Session", command=self.end_session, bg="lightcoral").pack(side=tk.LEFT, padx=5)
        self.session_label = tk.Label(session_frame, text="No active session", fg="gray")
        self.session_label.pack(side=tk.LEFT, padx=5)
        
        # Random Ring Button
        tk.Button(control_frame, text="Random Ring", command=self.random_ring, bg="lightblue").pack(side=tk.LEFT, padx=10)
        
        # Refresh Button
        tk.Button(control_frame, text="Refresh", command=self.update_dashboard).pack(side=tk.LEFT)
        
        # Student List Frame
        student_frame = tk.LabelFrame(middle_frame, text="Student Attendance", padx=5, pady=5)
        student_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Student Treeview
        self.tree = ttk.Treeview(student_frame, columns=("id", "name", "timer_status", "status", "time", "wifi", "attendance"), show="headings")
        self.tree.heading("id", text="Student ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("timer_status", text="Timer Status")
        self.tree.heading("status", text="Status")
        self.tree.heading("time", text="Time Left")
        self.tree.heading("wifi", text="WiFi Status")
        self.tree.heading("attendance", text="Attendance %")
        
        # Set column widths
        self.tree.column("id", width=100)
        self.tree.column("name", width=150)
        self.tree.column("timer_status", width=100)
        self.tree.column("status", width=100)
        self.tree.column("time", width=80)
        self.tree.column("wifi", width=100)
        self.tree.column("attendance", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Right-click menu for manual attendance
        self.tree_menu = tk.Menu(self.root, tearoff=0)
        self.tree_menu.add_command(label="Mark Present", command=lambda: self.manual_attendance_override("present"))
        self.tree_menu.add_command(label="Mark Absent", command=lambda: self.manual_attendance_override("absent"))
        
        self.tree.bind("<Button-3>", self.show_tree_menu)
    
    def setup_timetable_tab(self):
        # Timetable controls frame
        tt_controls = tk.Frame(self.timetable_frame)
        tt_controls.pack(fill=tk.X, pady=5)
        
        # Branch selection
        tk.Label(tt_controls, text="Branch:").pack(side=tk.LEFT)
        self.tt_branch_var = tk.StringVar()
        self.tt_branch_dropdown = ttk.Combobox(tt_controls, textvariable=self.tt_branch_var, 
                                             values=self.auth.current_teacher.get('branches', []))
        self.tt_branch_dropdown.pack(side=tk.LEFT, padx=5)
        self.tt_branch_dropdown.bind("<<ComboboxSelected>>", self.load_timetable_data)
        
        # Semester selection
        tk.Label(tt_controls, text="Semester:").pack(side=tk.LEFT)
        self.tt_semester_var = tk.StringVar()
        self.tt_semester_dropdown = ttk.Combobox(tt_controls, textvariable=self.tt_semester_var, 
                                               values=self.auth.current_teacher.get('semesters', []))
        self.tt_semester_dropdown.pack(side=tk.LEFT, padx=5)
        self.tt_semester_dropdown.bind("<<ComboboxSelected>>", self.load_timetable_data)
        
        # Special dates button
        tk.Button(tt_controls, text="Manage Special Dates", command=self.manage_special_dates).pack(side=tk.RIGHT, padx=5)
        
        # Timetable Treeview
        self.timetable_tree = ttk.Treeview(self.timetable_frame, columns=("day", "start", "end", "subject", "classroom"), show="headings")
        self.timetable_tree.heading("day", text="Day")
        self.timetable_tree.heading("start", text="Start Time")
        self.timetable_tree.heading("end", text="End Time")
        self.timetable_tree.heading("subject", text="Subject")
        self.timetable_tree.heading("classroom", text="Classroom")
        
        self.timetable_tree.column("day", width=100)
        self.timetable_tree.column("start", width=80)
        self.timetable_tree.column("end", width=80)
        self.timetable_tree.column("subject", width=150)
        self.timetable_tree.column("classroom", width=100)
        
        self.timetable_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Timetable Controls
        tt_buttons = tk.Frame(self.timetable_frame)
        tt_buttons.pack(fill=tk.X, pady=5)
        
        tk.Button(tt_buttons, text="Add Slot", command=self.add_timetable_slot).pack(side=tk.LEFT, padx=2)
        tk.Button(tt_buttons, text="Remove Slot", command=self.remove_timetable_slot).pack(side=tk.LEFT, padx=2)
        tk.Button(tt_buttons, text="Clear All", command=self.clear_timetable).pack(side=tk.LEFT, padx=2)
        tk.Button(tt_buttons, text="Save Timetable", command=self.save_timetable).pack(side=tk.RIGHT, padx=2)
        
        # Load timetable data
        self.load_timetable_data()
    
    def setup_students_tab(self):
        # Student controls frame
        controls_frame = tk.Frame(self.students_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Filter controls
        tk.Label(controls_frame, text="Classroom:").pack(side=tk.LEFT)
        self.student_classroom_var = tk.StringVar()
        self.student_classroom_dropdown = ttk.Combobox(controls_frame, textvariable=self.student_classroom_var, 
                                                      values=self.auth.current_teacher.get('classrooms', []))
        self.student_classroom_dropdown.pack(side=tk.LEFT, padx=5)
        self.student_classroom_dropdown.bind("<<ComboboxSelected>>", self.load_student_data)
        
        tk.Label(controls_frame, text="Branch:").pack(side=tk.LEFT)
        self.student_branch_var = tk.StringVar()
        self.student_branch_dropdown = ttk.Combobox(controls_frame, textvariable=self.student_branch_var, 
                                                  values=self.auth.current_teacher.get('branches', []))
        self.student_branch_dropdown.pack(side=tk.LEFT, padx=5)
        self.student_branch_dropdown.bind("<<ComboboxSelected>>", self.load_student_data)
        
        tk.Label(controls_frame, text="Semester:").pack(side=tk.LEFT)
        self.student_semester_var = tk.StringVar()
        self.student_semester_dropdown = ttk.Combobox(controls_frame, textvariable=self.student_semester_var, 
                                                     values=self.auth.current_teacher.get('semesters', []))
        self.student_semester_dropdown.pack(side=tk.LEFT, padx=5)
        self.student_semester_dropdown.bind("<<ComboboxSelected>>", self.load_student_data)
        
        tk.Button(controls_frame, text="Refresh", command=self.load_student_data).pack(side=tk.LEFT, padx=10)
        tk.Button(controls_frame, text="Register New", command=self.show_student_registration).pack(side=tk.RIGHT, padx=5)
        
        # Student Treeview
        student_tree_frame = tk.Frame(self.students_frame)
        student_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.student_tree = ttk.Treeview(student_tree_frame, columns=("id", "name", "classroom", "branch", "semester"), show="headings")
        self.student_tree.heading("id", text="Student ID")
        self.student_tree.heading("name", text="Name")
        self.student_tree.heading("classroom", text="Classroom")
        self.student_tree.heading("branch", text="Branch")
        self.student_tree.heading("semester", text="Semester")
        
        self.student_tree.column("id", width=100)
        self.student_tree.column("name", width=150)
        self.student_tree.column("classroom", width=100)
        self.student_tree.column("branch", width=80)
        self.student_tree.column("semester", width=80)
        
        self.student_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(student_tree_frame, orient="vertical", command=self.student_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        
        # Right-click menu for student actions
        self.student_tree_menu = tk.Menu(self.root, tearoff=0)
        self.student_tree_menu.add_command(label="Edit Student", command=self.edit_student)
        self.student_tree_menu.add_command(label="Delete Student", command=self.delete_student)
        self.student_tree_menu.add_command(label="View Attendance", command=self.view_student_attendance)
        
        self.student_tree.bind("<Button-3>", self.show_student_tree_menu)
        
        # Load initial student data
        self.load_student_data()
    
    def setup_reports_tab(self):
        # Report controls frame
        controls_frame = tk.Frame(self.reports_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(controls_frame, text="Student ID:").pack(side=tk.LEFT)
        self.report_student_id = tk.Entry(controls_frame, width=15)
        self.report_student_id.pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls_frame, text="From:").pack(side=tk.LEFT)
        self.report_from_date = tk.Entry(controls_frame, width=12)
        self.report_from_date.pack(side=tk.LEFT, padx=5)
        self.report_from_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(controls_frame, text="To:").pack(side=tk.LEFT)
        self.report_to_date = tk.Entry(controls_frame, width=12)
        self.report_to_date.pack(side=tk.LEFT, padx=5)
        self.report_to_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Button(controls_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=10)
        
        # Report display area
        report_display = tk.Frame(self.reports_frame)
        report_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Text widget for report
        self.report_text = tk.Text(report_display, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.report_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.report_text.yview)
    
    def setup_settings_tab(self):
        # Teacher Profile Frame
        profile_frame = tk.LabelFrame(self.settings_frame, text="Teacher Profile", padx=10, pady=10)
        profile_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(profile_frame, text="Teacher ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.profile_id = tk.Label(profile_frame, text=self.auth.current_teacher['id'])
        self.profile_id.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(profile_frame, text="Name:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.profile_name = tk.Entry(profile_frame)
        self.profile_name.insert(0, self.auth.current_teacher['name'])
        self.profile_name.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(profile_frame, text="Email:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.profile_email = tk.Entry(profile_frame)
        self.profile_email.insert(0, self.auth.current_teacher['email'])
        self.profile_email.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        tk.Button(profile_frame, text="Update Profile", command=self.update_profile).grid(row=3, columnspan=2, pady=10)
        
        # Change Password Frame
        password_frame = tk.LabelFrame(self.settings_frame, text="Change Password", padx=10, pady=10)
        password_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(password_frame, text="Current Password:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.current_password = tk.Entry(password_frame, show="*")
        self.current_password.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(password_frame, text="New Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.new_password = tk.Entry(password_frame, show="*")
        self.new_password.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(password_frame, text="Confirm New Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.confirm_password = tk.Entry(password_frame, show="*")
        self.confirm_password.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        tk.Button(password_frame, text="Change Password", command=self.change_password).grid(row=3, columnspan=2, pady=10)
        
        # BSSID Settings Frame
        bssid_frame = tk.LabelFrame(self.settings_frame, text="Classroom BSSID Settings", padx=10, pady=10)
        bssid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Classroom selection
        tk.Label(bssid_frame, text="Classroom:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.classroom_var = tk.StringVar()
        self.classroom_dropdown = ttk.Combobox(bssid_frame, textvariable=self.classroom_var)
        self.classroom_dropdown.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # BSSID entry
        tk.Label(bssid_frame, text="BSSID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.bssid_setting_entry = tk.Entry(bssid_frame)
        self.bssid_setting_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        tk.Button(bssid_frame, text="Load Settings", command=self.load_bssid_settings).grid(row=2, column=0, pady=10)
        tk.Button(bssid_frame, text="Save Settings", command=self.save_bssid_settings).grid(row=2, column=1, pady=10)
        
        # Classroom list
        self.classroom_list = tk.Listbox(bssid_frame)
        self.classroom_list.grid(row=3, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(bssid_frame)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.classroom_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.classroom_list.yview)
        
        # Configure grid weights
        bssid_frame.grid_rowconfigure(3, weight=1)
        bssid_frame.grid_columnconfigure(1, weight=1)
        
        # Load initial data
        self.load_classroom_data()
    
    def get_timetable_key(self):
        """Get the key for the current timetable view (branch/semester)"""
        branch = self.tt_branch_var.get()
        semester = self.tt_semester_var.get()
        
        if branch and semester:
            return f"{branch}_{semester}"
        return "default"
    
    def load_timetable_data(self, event=None):
        """Load timetable data into treeview based on current branch/semester"""
        timetable_key = self.get_timetable_key()
        
        # Clear existing items
        for item in self.timetable_tree.get_children():
            self.timetable_tree.delete(item)
        
        # Load data from server
        success, timetable = self.auth.get_timetable(
            self.tt_branch_var.get(),
            self.tt_semester_var.get()
        )
        
        if success:
            for slot in timetable:
                self.timetable_tree.insert("", "end", values=slot)
    
    def add_timetable_slot(self):
        """Add a new timetable slot"""
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Timetable Slot")
        
        tk.Label(add_window, text="Day:").grid(row=0, column=0, padx=5, pady=5)
        day_var = tk.StringVar()
        day_dropdown = ttk.Combobox(add_window, textvariable=day_var, 
                                   values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        day_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(add_window, text="Start Time (HH:MM):").grid(row=1, column=0, padx=5, pady=5)
        start_entry = tk.Entry(add_window)
        start_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(add_window, text="End Time (HH:MM):").grid(row=2, column=0, padx=5, pady=5)
        end_entry = tk.Entry(add_window)
        end_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(add_window, text="Subject:").grid(row=3, column=0, padx=5, pady=5)
        subject_entry = tk.Entry(add_window)
        subject_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(add_window, text="Classroom:").grid(row=4, column=0, padx=5, pady=5)
        classroom_entry = ttk.Combobox(add_window, values=self.auth.current_teacher.get('classrooms', []))
        classroom_entry.grid(row=4, column=1, padx=5, pady=5)
        
        def save_slot():
            day = day_var.get()
            start = start_entry.get()
            end = end_entry.get()
            subject = subject_entry.get()
            classroom = classroom_entry.get()
            
            if not all([day, start, end, subject, classroom]):
                messagebox.showwarning("Warning", "All fields are required")
                return
            
            try:
                # Validate time format
                datetime.strptime(start, "%H:%M")
                datetime.strptime(end, "%H:%M")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid time format. Use HH:MM")
                return
            
            self.timetable_tree.insert("", "end", values=(day, start, end, subject, classroom))
            add_window.destroy()
        
        tk.Button(add_window, text="Add Slot", command=save_slot).grid(row=5, columnspan=2, pady=10)
    
    def remove_timetable_slot(self):
        """Remove selected timetable slot"""
        selected = self.timetable_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a slot to remove")
            return
        
        for item in selected:
            self.timetable_tree.delete(item)
    
    def clear_timetable(self):
        """Clear all timetable slots for current view"""
        if messagebox.askyesno("Confirm", "Clear timetable for current branch/semester?"):
            for item in self.timetable_tree.get_children():
                self.timetable_tree.delete(item)
    
    def save_timetable(self):
        """Save timetable to server"""
        timetable_key = self.get_timetable_key()
        
        # Get all slots from the treeview
        timetable_slots = []
        for item in self.timetable_tree.get_children():
            timetable_slots.append(self.timetable_tree.item(item, 'values'))
        
        # Save to server
        success, message = self.auth.update_timetable(
            self.tt_branch_var.get(),
            self.tt_semester_var.get(),
            timetable_slots
        )
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
    
    def manage_special_dates(self):
        """Manage special dates (holidays and special schedules)"""
        special_window = tk.Toplevel(self.root)
        special_window.title("Manage Special Dates")
        special_window.geometry("600x400")
        
        # Notebook for holidays and special schedules
        notebook = ttk.Notebook(special_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Holidays tab
        holidays_frame = tk.Frame(notebook)
        notebook.add(holidays_frame, text="Holidays")
        
        # Holidays list
        holidays_list_frame = tk.Frame(holidays_frame)
        holidays_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.holidays_list = tk.Listbox(holidays_list_frame)
        self.holidays_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = tk.Scrollbar(holidays_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.holidays_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.holidays_list.yview)
        
        # Holidays controls
        holidays_controls = tk.Frame(holidays_frame)
        holidays_controls.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(holidays_controls, text="Date (YYYY-MM-DD):").pack(side=tk.LEFT)
        self.holiday_date_entry = tk.Entry(holidays_controls, width=12)
        self.holiday_date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(holidays_controls, text="Description:").pack(side=tk.LEFT)
        self.holiday_desc_entry = tk.Entry(holidays_controls)
        self.holiday_desc_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        tk.Button(holidays_controls, text="Add", command=self.add_holiday).pack(side=tk.LEFT, padx=5)
        tk.Button(holidays_controls, text="Remove", command=self.remove_holiday).pack(side=tk.LEFT, padx=5)
        
        # Special schedules tab
        special_sched_frame = tk.Frame(notebook)
        notebook.add(special_sched_frame, text="Special Schedules")
        
        # Special schedules list
        sched_list_frame = tk.Frame(special_sched_frame)
        sched_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.special_sched_list = tk.Listbox(sched_list_frame)
        self.special_sched_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = tk.Scrollbar(sched_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.special_sched_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.special_sched_list.yview)
        
        # Special schedule controls
        sched_controls = tk.Frame(special_sched_frame)
        sched_controls.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(sched_controls, text="Date (YYYY-MM-DD):").pack(side=tk.LEFT)
        self.sched_date_entry = tk.Entry(sched_controls, width=12)
        self.sched_date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(sched_controls, text="Description:").pack(side=tk.LEFT)
        self.sched_desc_entry = tk.Entry(sched_controls)
        self.sched_desc_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        tk.Button(sched_controls, text="Add", command=self.add_special_schedule).pack(side=tk.LEFT, padx=5)
        tk.Button(sched_controls, text="Remove", command=self.remove_special_schedule).pack(side=tk.LEFT, padx=5)
        
        # Save button
        tk.Button(special_window, text="Save Changes", command=lambda: [self.save_special_dates(), special_window.destroy()]).pack(pady=10)
        
        # Load current data
        self.load_holidays_list()
        self.load_special_schedules_list()
    
    def load_holidays_list(self):
        """Load holidays into the listbox"""
        self.holidays_list.delete(0, tk.END)
        for holiday in self.special_dates["holidays"]:
            self.holidays_list.insert(tk.END, f"{holiday['date']}: {holiday['description']}")
    
    def load_special_schedules_list(self):
        """Load special schedules into the listbox"""
        self.special_sched_list.delete(0, tk.END)
        for sched in self.special_dates["special_schedules"]:
            self.special_sched_list.insert(tk.END, f"{sched['date']}: {sched['description']}")
    
    def add_holiday(self):
        """Add a new holiday"""
        date = self.holiday_date_entry.get()
        description = self.holiday_desc_entry.get()
        
        if not date or not description:
            messagebox.showwarning("Warning", "Date and description are required")
            return
        
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Warning", "Invalid date format. Use YYYY-MM-DD")
            return
        
        # Check if date already exists
        if any(h['date'] == date for h in self.special_dates["holidays"]):
            messagebox.showwarning("Warning", "This date is already marked as a holiday")
            return
        
        self.special_dates["holidays"].append({"date": date, "description": description})
        self.load_holidays_list()
        
        # Clear fields
        self.holiday_date_entry.delete(0, tk.END)
        self.holiday_desc_entry.delete(0, tk.END)
    
    def remove_holiday(self):
        """Remove selected holiday"""
        selection = self.holidays_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a holiday to remove")
            return
        
        index = selection[0]
        del self.special_dates["holidays"][index]
        self.load_holidays_list()
    
    def add_special_schedule(self):
        """Add a new special schedule"""
        date = self.sched_date_entry.get()
        description = self.sched_desc_entry.get()
        
        if not date or not description:
            messagebox.showwarning("Warning", "Date and description are required")
            return
        
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Warning", "Invalid date format. Use YYYY-MM-DD")
            return
        
        # Check if date already exists
        if any(s['date'] == date for s in self.special_dates["special_schedules"]):
            messagebox.showwarning("Warning", "This date already has a special schedule")
            return
        
        self.special_dates["special_schedules"].append({"date": date, "description": description})
        self.load_special_schedules_list()
        
        # Clear fields
        self.sched_date_entry.delete(0, tk.END)
        self.sched_desc_entry.delete(0, tk.END)
    
    def remove_special_schedule(self):
        """Remove selected special schedule"""
        selection = self.special_sched_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a schedule to remove")
            return
        
        index = selection[0]
        del self.special_dates["special_schedules"][index]
        self.load_special_schedules_list()
    
    def save_special_dates(self):
        """Save special dates to server"""
        success, message = self.auth.update_special_dates(
            self.special_dates["holidays"],
            self.special_dates["special_schedules"]
        )
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
    
    def start_session(self):
        """Start a new class session"""
        if not self.current_classroom:
            messagebox.showwarning("Warning", "Please select a classroom first")
            return
            
        if self.current_session:
            messagebox.showinfo("Info", "A session is already active")
            return
        
        # Check if today is a holiday
        today = datetime.now().strftime("%Y-%m-%d")
        if any(h['date'] == today for h in self.special_dates["holidays"]):
            if not messagebox.askyesno("Confirm", "Today is marked as a holiday. Start session anyway?"):
                return
        
        # Get current day and time
        now = datetime.now()
        current_day = now.strftime("%A")
        current_time = now.strftime("%H:%M")
        
        # Find matching timetable slots for current classroom, branch, and semester
        matching_slots = []
        timetable_key = self.get_timetable_key()
        
        success, timetable = self.auth.get_timetable(self.current_branch, self.current_semester)
        if success:
            for slot in timetable:
                day, start, end, subject, classroom = slot
                if day == current_day and classroom == self.current_classroom:
                    try:
                        start_time = datetime.strptime(start, "%H:%M").time()
                        end_time = datetime.strptime(end, "%H:%M").time()
                        current_t = now.time()
                        
                        if start_time <= current_t <= end_time:
                            matching_slots.append((subject, start, end))
                    except ValueError:
                        continue
        
        if not matching_slots:
            if messagebox.askyesno("Confirm", "No scheduled class at this time. Start ad-hoc session?"):
                subject = simpledialog.askstring("Subject", "Enter subject name:")
                if not subject:
                    return
                
                try:
                    response = requests.post(
                        f"{self.server_url}/teacher/start_session",
                        json={
                            'teacher_id': self.auth.current_teacher['id'],
                            'classroom': self.current_classroom,
                            'subject': subject,
                            'branch': self.current_branch,
                            'semester': self.current_semester,
                            'ad_hoc': True
                        }
                    )
                    
                    if response.status_code == 201:
                        self.current_session = {
                            "id": response.json()['session_id'],
                            "subject": subject,
                            "classroom": self.current_classroom,
                            "branch": self.current_branch,
                            "semester": self.current_semester,
                            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "ad_hoc": True
                        }
                        
                        self.session_label.config(text=f"Session: {subject} (Ad-hoc)", fg="green")
                        teacher_info = self.auth.current_teacher
                        self.status_label.config(
                            text=f"Teacher: {teacher_info['name']} ({teacher_info['id']}) | Classroom: {self.current_classroom} | Branch/Semester: {self.current_branch or 'None'}/{self.current_semester or 'None'} | Session: {subject} (Active)"
                        )
                        messagebox.showinfo("Session Started", f"{subject} session started at {self.current_session['start_time']}")
                    else:
                        messagebox.showerror("Error", response.json().get('error', 'Failed to start session'))
                except requests.exceptions.RequestException:
                    messagebox.showerror("Error", "Could not connect to server")
            return
        
        # If multiple slots match (unlikely), let teacher choose
        if len(matching_slots) > 1:
            subject = simpledialog.askstring("Select Subject", 
                                           f"Multiple classes running:\n{', '.join([s[0] for s in matching_slots])}\nEnter subject:")
            if not subject:
                return
        else:
            subject = matching_slots[0][0]
        
        try:
            response = requests.post(
                f"{self.server_url}/teacher/start_session",
                json={
                    'teacher_id': self.auth.current_teacher['id'],
                    'classroom': self.current_classroom,
                    'subject': subject,
                    'branch': self.current_branch,
                    'semester': self.current_semester,
                    'ad_hoc': False
                }
            )
            
            if response.status_code == 201:
                self.current_session = {
                    "id": response.json()['session_id'],
                    "subject": subject,
                    "classroom": self.current_classroom,
                    "branch": self.current_branch,
                    "semester": self.current_semester,
                    "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ad_hoc": False
                }
                
                self.session_label.config(text=f"Session: {subject}", fg="green")
                teacher_info = self.auth.current_teacher
                self.status_label.config(
                    text=f"Teacher: {teacher_info['name']} ({teacher_info['id']}) | Classroom: {self.current_classroom} | Branch/Semester: {self.current_branch or 'None'}/{self.current_semester or 'None'} | Session: {subject} (Active)"
                )
                messagebox.showinfo("Session Started", f"{subject} session started at {self.current_session['start_time']}")
            else:
                messagebox.showerror("Error", response.json().get('error', 'Failed to start session'))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")
    
    def end_session(self):
        """End the current class session"""
        if not self.current_session:
            messagebox.showinfo("Info", "No active session to end")
            return
        
        try:
            response = requests.post(
                f"{self.server_url}/teacher/end_session",
                json={
                    'session_id': self.current_session['id']
                }
            )
            
            if response.status_code == 200:
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                messagebox.showinfo("Session Ended", 
                                  f"{self.current_session['subject']} session ended.\n"
                                  f"Started: {self.current_session['start_time']}\n"
                                  f"Ended: {end_time}")
                
                self.current_session = None
                self.session_label.config(text="No active session", fg="gray")
                teacher_info = self.auth.current_teacher
                self.status_label.config(
                    text=f"Teacher: {teacher_info['name']} ({teacher_info['id']}) | Classroom: {self.current_classroom} | Branch/Semester: {self.current_branch or 'None'}/{self.current_semester or 'None'} | Session: Not active"
                )
            else:
                messagebox.showerror("Error", response.json().get('error', 'Failed to end session'))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")
    
    def set_bssid(self):
        bssid = self.bssid_entry.get()
        if not bssid:
            messagebox.showwarning("Warning", "Please enter a BSSID")
            return
        
        try:
            response = requests.post(
                f"{self.server_url}/teacher/set_bssid",
                json={"bssid": bssid}
            )
            if response.status_code == 200:
                messagebox.showinfo("Success", response.json()["message"])
                teacher_info = self.auth.current_teacher
                self.status_label.config(
                    text=f"Teacher: {teacher_info['name']} ({teacher_info['id']}) | Classroom: {self.current_classroom} | Branch/Semester: {self.current_branch or 'None'}/{self.current_semester or 'None'} | Session: {'Active' if self.current_session else 'Not active'}"
                )
            else:
                messagebox.showerror("Error", response.json().get("error", "Failed to set BSSID"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")
    
    def show_student_registration(self):
        """Show student registration dialog"""
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Register Student")
        reg_window.geometry("400x300")
        
        tk.Label(reg_window, text="Student ID:").pack(pady=(20, 5))
        student_id_entry = tk.Entry(reg_window)
        student_id_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Password:").pack(pady=5)
        password_entry = tk.Entry(reg_window, show="*")
        password_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Name:").pack(pady=5)
        name_entry = tk.Entry(reg_window)
        name_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Classroom:").pack(pady=5)
        classroom_entry = ttk.Combobox(reg_window, values=self.auth.current_teacher.get('classrooms', []))
        classroom_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Branch:").pack(pady=5)
        branch_entry = ttk.Combobox(reg_window, values=self.auth.current_teacher.get('branches', []))
        branch_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Semester:").pack(pady=5)
        semester_entry = ttk.Combobox(reg_window, values=self.auth.current_teacher.get('semesters', []))
        semester_entry.pack(pady=5)
        
        def register():
            student_id = student_id_entry.get()
            password = password_entry.get()
            name = name_entry.get()
            classroom = classroom_entry.get()
            branch = branch_entry.get()
            semester = semester_entry.get()
            
            if not all([student_id, password, name, classroom, branch, semester]):
                messagebox.showwarning("Warning", "All fields are required")
                return
            
            success, message = self.auth.register_student(student_id, password, name, classroom, branch, semester)
            if success:
                messagebox.showinfo("Success", message)
                reg_window.destroy()
                self.load_student_data()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(reg_window, text="Register", command=register).pack(pady=20)
    
    def select_classroom(self):
        """Select classroom dialog"""
        classrooms = self.auth.current_teacher.get('classrooms', [])
        if not classrooms:
            messagebox.showwarning("Warning", "No classrooms configured. Please add classrooms in settings.")
            return
            
        select_window = tk.Toplevel(self.root)
        select_window.title("Select Classroom")
        
        tk.Label(select_window, text="Select Classroom:").pack(pady=10)
        
        classroom_var = tk.StringVar()
        classroom_dropdown = ttk.Combobox(select_window, textvariable=classroom_var, values=classrooms)
        classroom_dropdown.pack(pady=5)
        
        def select():
            classroom = classroom_var.get()
            if not classroom:
                messagebox.showwarning("Warning", "Please select a classroom")
                return
                
            self.current_classroom = classroom
            teacher_info = self.auth.current_teacher
            self.status_label.config(
                text=f"Teacher: {teacher_info['name']} ({teacher_info['id']}) | Classroom: {self.current_classroom} | Branch/Semester: {self.current_branch or 'None'}/{self.current_semester or 'None'} | Session: {'Active' if self.current_session else 'Not active'}"
            )
            
            # Set BSSID if available
            bssid = self.auth.current_teacher['bssid_mapping'].get(classroom, "")
            self.bssid_entry.delete(0, tk.END)
            self.bssid_entry.insert(0, bssid)
            
            select_window.destroy()
            messagebox.showinfo("Success", f"Classroom {classroom} selected")
        
        tk.Button(select_window, text="Select", command=select).pack(pady=10)
    
    def select_branch_semester(self):
        """Select branch and semester dialog"""
        select_window = tk.Toplevel(self.root)
        select_window.title("Select Branch and Semester")
        
        tk.Label(select_window, text="Branch:").grid(row=0, column=0, padx=5, pady=5)
        branch_var = tk.StringVar()
        branch_dropdown = ttk.Combobox(select_window, textvariable=branch_var, 
                                     values=self.auth.current_teacher.get('branches', []))
        branch_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(select_window, text="Semester:").grid(row=1, column=0, padx=5, pady=5)
        semester_var = tk.StringVar()
        semester_dropdown = ttk.Combobox(select_window, textvariable=semester_var, 
                                       values=self.auth.current_teacher.get('semesters', []))
        semester_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        def select():
            branch = branch_var.get()
            semester = semester_var.get()
            
            if not branch or not semester:
                messagebox.showwarning("Warning", "Please select both branch and semester")
                return
                
            self.current_branch = branch
            self.current_semester = semester
            teacher_info = self.auth.current_teacher
            self.status_label.config(
                text=f"Teacher: {teacher_info['name']} ({teacher_info['id']}) | Classroom: {self.current_classroom or 'Not selected'} | Branch/Semester: {self.current_branch}/{self.current_semester} | Session: {'Active' if self.current_session else 'Not active'}"
            )
            
            # Update timetable view
            self.tt_branch_var.set(branch)
            self.tt_semester_var.set(semester)
            self.load_timetable_data()
            
            select_window.destroy()
            messagebox.showinfo("Success", f"Branch/Semester {branch}/{semester} selected")
        
        tk.Button(select_window, text="Select", command=select).grid(row=2, columnspan=2, pady=10)
    
    def load_student_data(self, event=None):
        """Load student data based on current filters"""
        classroom = self.student_classroom_var.get()
        branch = self.student_branch_var.get()
        semester = self.student_semester_var.get()
        
        students = self.auth.get_students(classroom=classroom, branch=branch, semester=semester)
        
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Add students to treeview
        for student in students:
            self.student_tree.insert("", "end", values=(
                student['id'],
                student['name'],
                student['classroom'],
                student['branch'],
                student['semester']
            ))
    
    def show_student_tree_menu(self, event):
        """Show right-click menu for student treeview"""
        item = self.student_tree.identify_row(event.y)
        if item:
            self.student_tree.selection_set(item)
            self.current_selected_student = self.student_tree.item(item, "values")[0]
            self.student_tree_menu.post(event.x_root, event.y_root)
    
    def edit_student(self):
        """Edit selected student"""
        if not hasattr(self, 'current_selected_student'):
            return
            
        student_id = self.current_selected_student
        students = self.auth.get_students()
        student = next((s for s in students if s['id'] == student_id), None)
        
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Student")
        edit_window.geometry("400x300")
        
        tk.Label(edit_window, text="Student ID:").pack(pady=(20, 5))
        student_id_label = tk.Label(edit_window, text=student['id'])
        student_id_label.pack(pady=5)
        
        tk.Label(edit_window, text="Name:").pack(pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.insert(0, student['name'])
        name_entry.pack(pady=5)
        
        tk.Label(edit_window, text="Classroom:").pack(pady=5)
        classroom_entry = ttk.Combobox(edit_window, values=self.auth.current_teacher.get('classrooms', []))
        classroom_entry.set(student['classroom'])
        classroom_entry.pack(pady=5)
        
        tk.Label(edit_window, text="Branch:").pack(pady=5)
        branch_entry = ttk.Combobox(edit_window, values=self.auth.current_teacher.get('branches', []))
        branch_entry.set(student['branch'])
        branch_entry.pack(pady=5)
        
        tk.Label(edit_window, text="Semester:").pack(pady=5)
        semester_entry = ttk.Combobox(edit_window, values=self.auth.current_teacher.get('semesters', []))
        semester_entry.set(student['semester'])
        semester_entry.pack(pady=5)
        
        def save_changes():
            new_data = {
                'name': name_entry.get(),
                'classroom': classroom_entry.get(),
                'branch': branch_entry.get(),
                'semester': semester_entry.get()
            }
            
            if not all(new_data.values()):
                messagebox.showwarning("Warning", "All fields are required")
                return
            
            success, message = self.auth.update_student(student_id, new_data)
            if success:
                messagebox.showinfo("Success", message)
                edit_window.destroy()
                self.load_student_data()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(edit_window, text="Save Changes", command=save_changes).pack(pady=20)
    
    def delete_student(self):
        """Delete selected student"""
        if not hasattr(self, 'current_selected_student'):
            return
            
        student_id = self.current_selected_student
        
        if messagebox.askyesno("Confirm", f"Delete student {student_id}? This cannot be undone."):
            success, message = self.auth.delete_student(student_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_student_data()
            else:
                messagebox.showerror("Error", message)
    
    def view_student_attendance(self):
        """View attendance records for selected student"""
        if not hasattr(self, 'current_selected_student'):
            return
            
        student_id = self.current_selected_student
        students = self.auth.get_students()
        student = next((s for s in students if s['id'] == student_id), None)
        
        if not student:
            messagebox.showerror("Error", "Student not found")
            return
        
        attendance_window = tk.Toplevel(self.root)
        attendance_window.title(f"Attendance for {student['name']} ({student_id})")
        attendance_window.geometry("800x600")
        
        # Create treeview for attendance records
        attendance_tree = ttk.Treeview(attendance_window, columns=("date", "subject", "status", "time"), show="headings")
        attendance_tree.heading("date", text="Date")
        attendance_tree.heading("subject", text="Subject")
        attendance_tree.heading("status", text="Status")
        attendance_tree.heading("time", text="Time")
        
        attendance_tree.column("date", width=100)
        attendance_tree.column("subject", width=150)
        attendance_tree.column("status", width=80)
        attendance_tree.column("time", width=150)
        
        attendance_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add attendance records
        if 'attendance' in student:
            for date, sessions in student['attendance'].items():
                for session_key, session_data in sessions.items():
                    attendance_tree.insert("", "end", values=(
                        date,
                        session_data.get('subject', 'N/A'),
                        session_data.get('status', 'N/A'),
                        f"{session_data.get('start_time', '')} to {session_data.get('end_time', '')}"
                    ))
        
        # Calculate and show statistics
            stats_frame = tk.Frame(attendance_window)
            stats_frame.pack(fill=tk.X, padx=10, pady=5)

            if 'attendance' in student:
                total_sessions = sum(len(sessions) for sessions in student['attendance'].values())
                present_sessions = sum(1 for sessions in student['attendance'].values() 
                                    for session in sessions.values() if session.get('status') == 'present')
                attendance_percent = round((present_sessions / total_sessions) * 100 if total_sessions > 0 else 0, 2)
                
                tk.Label(stats_frame, text=f"Total Sessions: {total_sessions}").pack(side=tk.LEFT, padx=10)
                tk.Label(stats_frame, text=f"Present: {present_sessions}").pack(side=tk.LEFT, padx=10)
                tk.Label(stats_frame, text=f"Attendance Percentage: {attendance_percent}%").pack(side=tk.LEFT, padx=10)
            else:
                tk.Label(stats_frame, text="No attendance records found").pack(side=tk.LEFT, padx=10)
    
    def update_dashboard(self):
        try:
            response = requests.get(
                f"{self.server_url}/teacher/get_status",
                params={'classroom': self.current_classroom} if self.current_classroom else {}
            )
            if response.status_code == 200:
                data = response.json()
                self.update_student_list(data)
                self.update_attendance_records(data)
        except requests.exceptions.RequestException as e:
            print(f"Error updating dashboard: {e}")
    
    def update_attendance_records(self, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for student_id, student in data["students"].items():
            if student_id not in self.student_attendance:
                self.student_attendance[student_id] = []
            
            # Record present/absent status only during active session
            if self.current_session:
                # Check if there's a manual override
                if student_id in self.manual_overrides:
                    is_present = self.manual_overrides[student_id] == "present"
                else:
                    timer_status = student["timer"]["status"].lower()
                    is_present = timer_status == "running"
                
                self.student_attendance[student_id].append((current_time, is_present))
    
    def update_student_list(self, data):
        self.tree.delete(*self.tree.get_children())
        
        authorized_bssid = data["authorized_bssid"] or "Not set"
        session_text = f"{self.current_session['subject']} (Active)" if self.current_session else "Not active"
        teacher_info = self.auth.current_teacher
        self.status_label.config(
            text=f"Teacher: {teacher_info['name']} ({teacher_info['id']}) | Classroom: {self.current_classroom or 'Not selected'} | Branch/Semester: {self.current_branch or 'None'}/{self.current_semester or 'None'} | Session: {session_text}"
        )
        
        for student_id, student in data["students"].items():
            timer = student["timer"]
            
            # Format time
            mins, secs = divmod(int(timer["remaining"]), 60)
            time_str = f"{mins:02d}:{secs:02d}" if timer["remaining"] > 0 else "00:00"
            
            # WiFi status
            wifi_status = "Authorized" if student["authorized"] else "Unauthorized" if student["connected"] else "Disconnected"
            
            # Determine status based on timer status or manual override
            if student_id in self.manual_overrides:
                student_status = "Present" if self.manual_overrides[student_id] == "present" else "Absent"
            else:
                timer_status = timer["status"].lower()
                if timer_status in ("stop", "pause"):
                    student_status = "Absent"
                elif timer_status == "running":
                    student_status = "Present"
                elif timer_status == "completed":
                    student_status = "Pending"
                else:
                    student_status = "Unknown"
            
            # Calculate attendance percentage
            attendance_percent = self.calculate_attendance(student_id)
            
            self.tree.insert("", "end", values=(
                student_id,
                student.get("name", ""),
                timer["status"].capitalize(),
                student_status,
                time_str,
                wifi_status,
                f"{attendance_percent}%"
            ), tags=(student_id,))
    
    def calculate_attendance(self, student_id):
        if student_id not in self.student_attendance or not self.student_attendance[student_id]:
            return 0
        
        total_records = len(self.student_attendance[student_id])
        present_count = sum(1 for record in self.student_attendance[student_id] if record[1])
        return round((present_count / total_records) * 100)
    
    def show_tree_menu(self, event):
        """Show right-click menu for treeview"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.current_selected_student = self.tree.item(item, "values")[0]
            self.tree_menu.post(event.x_root, event.y_root)
    
    def manual_attendance_override(self, status):
        """Manually override attendance status for a student"""
        if not hasattr(self, 'current_selected_student'):
            return
            
        student_id = self.current_selected_student
        
        if status == "absent":
            # Check if student was previously marked present
            if student_id not in self.manual_overrides or self.manual_overrides[student_id] != "present":
                messagebox.showwarning("Warning", "You can only mark absent for students you've previously marked present")
                return
        
        try:
            response = requests.post(
                f"{self.server_url}/teacher/manual_override",
                json={
                    'student_id': student_id,
                    'status': status
                }
            )
            
            if response.status_code == 200:
                self.manual_overrides[student_id] = status
                self.update_dashboard()
                messagebox.showinfo("Success", f"Student {student_id} marked as {status}")
            else:
                messagebox.showerror("Error", response.json().get('error', 'Failed to update status'))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")
    
    def random_ring(self):
        if not self.current_session:
            messagebox.showwarning("Warning", "No active session. Please start a session first.")
            return
            
        if not self.current_classroom:
            messagebox.showwarning("Warning", "No classroom selected. Please select a classroom first.")
            return
            
        try:
            response = requests.post(
                f"{self.server_url}/teacher/random_ring",
                params={'classroom': self.current_classroom}
            )
            
            if response.status_code == 200:
                data = response.json()
                low_student = data['low_attendance_student']
                high_student = data['high_attendance_student']
                
                # Create a dialog window for the random ring
                ring_window = tk.Toplevel(self.root)
                ring_window.title("Random Ring - Verify Attendance")
                ring_window.geometry("500x300")
                
                # Make the window stay on top
                ring_window.attributes('-topmost', True)
                ring_window.after(100, lambda: ring_window.attributes('-topmost', False))
                
                tk.Label(ring_window, text="Random Ring Results", font=('Helvetica', 14, 'bold')).pack(pady=10)
                
                # Frame for student 1 (low attendance)
                frame1 = tk.Frame(ring_window)
                frame1.pack(fill=tk.X, padx=10, pady=5)
                
                tk.Label(frame1, text=f"Low Attendance: {low_student['id']} ({low_student['attendance_percentage']}%)").pack(side=tk.LEFT)
                
                # Add tick/cross buttons for student 1
                def approve_student1():
                    # Just keep the current status
                    ring_window.destroy()
                    messagebox.showinfo("Approved", f"Student {low_student['id']} remains as marked")
                
                def punish_student1():
                    # Mark absent and deduct 1.5 lectures
                    try:
                        response = requests.post(
                            f"{self.server_url}/teacher/manual_override",
                            json={
                                'student_id': low_student['id'],
                                'status': 'absent'
                            }
                        )
                        
                        if response.status_code == 200:
                            # Add punishment record
                            punishment_date = datetime.now().strftime("%Y-%m-%d")
                            punishment_key = f"PUNISHMENT_{uuid.uuid4().hex}"

                            # Get student data
                            students = self.auth.get_students()
                            student_index = next((i for i, s in enumerate(students) if s['id'] == low_student['id']), None)
                            
                            if student_index is not None:
                                if 'attendance' not in students[student_index]:
                                    students[student_index]['attendance'] = {}
                                
                                if punishment_date not in students[student_index]['attendance']:
                                    students[student_index]['attendance'][punishment_date] = {}
                                
                                # Add punishment record (1.5 lectures)
                                students[student_index]['attendance'][punishment_date][punishment_key] = {
                                    "status": "absent",
                                    "subject": "PUNISHMENT",
                                    "classroom": self.current_classroom,
                                    "start_time": datetime.now().strftime("%H:%M:%S"),
                                    "end_time": (datetime.now() + timedelta(minutes=90)).strftime("%H:%M:%S"),
                                    "branch": self.current_branch,
                                    "semester": self.current_semester,
                                    "reason": "Random Ring Punishment"
                                }
                                
                                # Save the changes
                                try:
                                    response = requests.post(
                                        f"{self.server_url}/teacher/update_student",
                                        json={
                                            'id': low_student['id'],
                                            'new_data': {'attendance': students[student_index]['attendance']}
                                        }
                                    )
                                    
                                    if response.status_code == 200:
                                        self.manual_overrides[low_student['id']] = "absent"
                                        self.update_dashboard()
                                        ring_window.destroy()
                                        messagebox.showwarning("Punished", f"Student {low_student['id']} marked absent and penalized 1.5 lectures")
                                    else:
                                        messagebox.showerror("Error", response.json().get('error', 'Failed to update student'))
                                except requests.exceptions.RequestException:
                                    messagebox.showerror("Error", "Could not connect to server")
                            else:
                                messagebox.showerror("Error", "Student not found")
                        else:
                            messagebox.showerror("Error", response.json().get('error', 'Failed to mark student absent'))
                    except requests.exceptions.RequestException:
                        messagebox.showerror("Error", "Could not connect to server")
                
                tk.Button(frame1, text="✓", command=approve_student1, bg="green", fg="white").pack(side=tk.RIGHT, padx=5)
                tk.Button(frame1, text="✗", command=punish_student1, bg="red", fg="white").pack(side=tk.RIGHT)
                
                # Frame for student 2 (high attendance)
                frame2 = tk.Frame(ring_window)
                frame2.pack(fill=tk.X, padx=10, pady=5)
                
                tk.Label(frame2, text=f"High Attendance: {high_student['id']} ({high_student['attendance_percentage']}%)").pack(side=tk.LEFT)
                
                # Add tick/cross buttons for student 2
                def approve_student2():
                    # Just keep the current status
                    ring_window.destroy()
                    messagebox.showinfo("Approved", f"Student {high_student['id']} remains as marked")
                
                def punish_student2():
                    # Mark absent and deduct 1.5 lectures
                    try:
                        response = requests.post(
                            f"{self.server_url}/teacher/manual_override",
                            json={
                                'student_id': high_student['id'],
                                'status': 'absent'
                            }
                        )
                        
                        if response.status_code == 200:
                            # Add punishment record
                            punishment_date = datetime.now().strftime("%Y-%m-%d")
                            punishment_key = f"PUNISHMENT_{uuid.uuid4().hex}"
                            
                            # Get student data
                            students = self.auth.get_students()
                            student_index = next((i for i, s in enumerate(students) if s['id'] == high_student['id']), None)
                            
                            if student_index is not None:
                                if 'attendance' not in students[student_index]:
                                    students[student_index]['attendance'] = {}
                                
                                if punishment_date not in students[student_index]['attendance']:
                                    students[student_index]['attendance'][punishment_date] = {}
                                
                                # Add punishment record (1.5 lectures)
                                students[student_index]['attendance'][punishment_date][punishment_key] = {
                                    "status": "absent",
                                    "subject": "PUNISHMENT",
                                    "classroom": self.current_classroom,
                                    "start_time": datetime.now().strftime("%H:%M:%S"),
                                    "end_time": (datetime.now() + timedelta(minutes=90)).strftime("%H:%M:%S"),
                                    "branch": self.current_branch,
                                    "semester": self.current_semester,
                                    "reason": "Random Ring Punishment"
                                }
                                
                                # Save the changes
                                try:
                                    response = requests.post(
                                        f"{self.server_url}/teacher/update_student",
                                        json={
                                            'id': high_student['id'],
                                            'new_data': {'attendance': students[student_index]['attendance']}
                                        }
                                    )
                                    
                                    if response.status_code == 200:
                                        self.manual_overrides[high_student['id']] = "absent"
                                        self.update_dashboard()
                                        ring_window.destroy()
                                        messagebox.showwarning("Punished", f"Student {high_student['id']} marked absent and penalized 1.5 lectures")
                                    else:
                                        messagebox.showerror("Error", response.json().get('error', 'Failed to update student'))
                                except requests.exceptions.RequestException:
                                    messagebox.showerror("Error", "Could not connect to server")
                            else:
                                messagebox.showerror("Error", "Student not found")
                        else:
                            messagebox.showerror("Error", response.json().get('error', 'Failed to mark student absent'))
                    except requests.exceptions.RequestException:
                        messagebox.showerror("Error", "Could not connect to server")
                
                tk.Button(frame2, text="✓", command=approve_student2, bg="green", fg="white").pack(side=tk.RIGHT, padx=5)
                tk.Button(frame2, text="✗", command=punish_student2, bg="red", fg="white").pack(side=tk.RIGHT)
                
                # Highlight the selected students in the treeview
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    if values[0] == low_student['id']:
                        self.tree.item(item, tags=('low',))
                        self.tree.tag_configure('low', background='#ffcccc')  # Light red
                    elif values[0] == high_student['id']:
                        self.tree.item(item, tags=('high',))
                        self.tree.tag_configure('high', background='#ccffcc')  # Light green
            else:
                messagebox.showerror("Error", response.json().get('error', 'Random ring failed'))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to server")
    
    def generate_report(self):
        """Generate attendance report for a student"""
        student_id = self.report_student_id.get()
        from_date = self.report_from_date.get()
        to_date = self.report_to_date.get()
        
        if not student_id:
            messagebox.showwarning("Warning", "Please enter a Student ID")
            return
        
        try:
            # Validate dates
            datetime.strptime(from_date, "%Y-%m-%d")
            datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Warning", "Invalid date format. Use YYYY-MM-DD")
            return
        
        # Get student data
        students = self.auth.get_students()
        student = next((s for s in students if s['id'] == student_id), None)
        
        if not student:
            messagebox.showwarning("Warning", "Student not found")
            return
        
        if 'attendance' not in student or not student['attendance']:
            messagebox.showwarning("Warning", "No attendance records for this student")
            return
        
        # Filter records by date range
        filtered_records = []
        for date, sessions in student['attendance'].items():
            if from_date <= date <= to_date:
                for session_key, session_data in sessions.items():
                    filtered_records.append({
                        'date': date,
                        'subject': session_data.get('subject', 'N/A'),
                        'classroom': session_data.get('classroom', 'N/A'),
                        'status': session_data.get('status', 'N/A'),
                        'time': f"{session_data.get('start_time', '')} to {session_data.get('end_time', '')}"
                    })
        
        if not filtered_records:
            messagebox.showinfo("Info", "No attendance records in the selected date range")
            return
        
        # Calculate stats
        total_classes = len(filtered_records)
        present_count = sum(1 for r in filtered_records if r['status'] == 'present')
        attendance_percent = round((present_count / total_classes) * 100) if total_classes > 0 else 0
        
        # Generate report text
        report_text = f"ATTENDANCE REPORT FOR STUDENT {student_id} ({student['name']})\n"
        report_text += f"Branch: {student['branch']} | Semester: {student['semester']} | Classroom: {student['classroom']}\n"
        report_text += f"Date Range: {from_date} to {to_date}\n"
        report_text += f"Total Classes: {total_classes}\n"
        report_text += f"Present: {present_count}\n"
        report_text += f"Absent: {total_classes - present_count}\n"
        report_text += f"Attendance Percentage: {attendance_percent}%\n\n"
        report_text += "DETAILED RECORDS:\n"
        report_text += "Date       | Subject           | Classroom | Status  | Time\n"
        report_text += "------------------------------------------------------------\n"
        
        for record in filtered_records:
            report_text += f"{record['date']} | {record['subject'][:15].ljust(15)} | {record['classroom'].ljust(8)} | {record['status'].ljust(7)} | {record['time']}\n"
        
        # Display report
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report_text)
    
    def update_profile(self):
        """Update teacher profile"""
        name = self.profile_name.get()
        email = self.profile_email.get()
        
        if not name or not email:
            messagebox.showwarning("Warning", "Name and email are required")
            return
        
        success, message = self.auth.update_teacher_profile(
            self.auth.current_teacher['id'],
            {'name': name, 'email': email}
        )
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
    
    def change_password(self):
        """Change teacher password"""
        current_password = self.current_password.get()
        new_password = self.new_password.get()
        confirm_password = self.confirm_password.get()
        
        if not current_password or not new_password or not confirm_password:
            messagebox.showwarning("Warning", "All password fields are required")
            return
        
        if new_password != confirm_password:
            messagebox.showwarning("Warning", "New passwords don't match")
            return
        
        success, message = self.auth.change_teacher_password(
            self.auth.current_teacher['id'],
            current_password,
            new_password
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.current_password.delete(0, tk.END)
            self.new_password.delete(0, tk.END)
            self.confirm_password.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)
    
    def load_classroom_data(self):
        """Load classroom data into settings"""
        teacher = self.auth.current_teacher
        classrooms = teacher.get('classrooms', [])
        bssid_mapping = teacher.get('bssid_mapping', {})
        
        # Update dropdown
        self.classroom_dropdown['values'] = classrooms
        
        # Update listbox
        self.classroom_list.delete(0, tk.END)
        for classroom in classrooms:
            bssid = bssid_mapping.get(classroom, "Not set")
            self.classroom_list.insert(tk.END, f"{classroom}: {bssid}")
    
    def load_bssid_settings(self):
        """Load BSSID settings for selected classroom"""
        classroom = self.classroom_var.get()
        if not classroom:
            messagebox.showwarning("Warning", "Please select a classroom")
            return
        
        bssid = self.auth.current_teacher['bssid_mapping'].get(classroom, "")
        self.bssid_setting_entry.delete(0, tk.END)
        self.bssid_setting_entry.insert(0, bssid)
    
    def save_bssid_settings(self):
        """Save BSSID settings for classroom"""
        classroom = self.classroom_var.get()
        bssid = self.bssid_setting_entry.get()
        
        if not classroom:
            messagebox.showwarning("Warning", "Please select a classroom")
            return
        
        success, message = self.auth.update_bssid_mapping(
            self.auth.current_teacher['id'],
            classroom,
            bssid
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_classroom_data()
        else:
            messagebox.showerror("Error", message)
    
    def auto_refresh(self):
        self.update_dashboard()
        self.root.after(2000, self.auto_refresh)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    auth_system = TeacherAuth()
    LoginWindow(auth_system).run()
