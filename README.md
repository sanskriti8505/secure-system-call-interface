# User-Friendly System Call Interface for Enhanced Security

This project is an Operating Systems academic project demonstrating a secure system call interface using a web-based dashboard. It provides an intuitive interface for performing restricted actions (read, write, delete, execute) while enforcing role-based access control and comprehensive logging.

## Features
- **Secure Wrappers:** Safe execution of read, write, delete, and command execution.
- **Authentication:** Role-based access control (Admin & User).
- **Audit Logging:** Every action is logged to an SQLite database.
- **Modern UI:** "Dark cybersecurity" themed dashboard using Tailwind CSS.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to `http://127.0.0.1:5000/`.

## Default Users
The database is initialized automatically with two users:
- **Admin**: Username: `admin`, Password: `admin123` (Full permissions)
- **User**: Username: `user`, Password: `user123` (Read-only permissions)
Added authentication documentation 
Updated RBAC notes 
Added system call wrapper notes 
Added logging updates 
Updated dashboard notes 
Final optimization notes 
