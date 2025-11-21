# 📚 Face Recognition Attendance System

A Flask + MySQL based attendance system that uses Face Recognition to automatically mark student attendance. Built with a clean API structure, JWT authentication, and real-time updates using Socket.IO.

## 🚀 Features

### 👨‍🏫 Teacher Panel
- Signup & Login with secure authentication
- Start / Lock / Unlock / Stop attendance sessions
- View and export attendance records
- Real-time session management

### 👨‍🎓 Student Panel
- Signup & Login functionality
- Upload face image (stored & converted to embedding)
- Join session using session code
- Automatic attendance marking through face recognition

### 🔐 Security & Performance
- JWT-based authentication
- Face embedding comparison for accurate recognition
- Real-time updates via Flask-SocketIO
- Secure image storage and processing

## 🛠️ Technologies Used

- **Backend**: Python Flask
- **Database**: MySQL
- **Real-time Communication**: Flask-SocketIO
- **Authentication**: JWT (JSON Web Tokens)
- **Image Processing**: Pillow / OpenCV
- **Face Recognition**: Custom Face Embedding Model (`facerecog.py`)

## 📦 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/TimeSweaper/Automated-Attendance-System-using-Face-Recognition-QR-Verification.git
cd yourrepo
```

### 2️⃣ Create & Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Create Required Folders

```bash
mkdir -p uploads/teachers uploads/students
```

## 🗄️ MySQL Setup

### 1. Create a Database

```sql
CREATE DATABASE attendance_db;
```

### 2. Configure Database Credentials

Edit the file: `Database/DB_Data.py`

Example configuration:
```python
mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="attendance_db"
)
```

### 3. Required Tables

The system requires the following tables:
- `teachers` - Store teacher account information
- `students` - Store student account information
- `sessions` - Track attendance sessions
- `attendance` - Record attendance entries

> **Note**: Table schemas are defined in the queries within `DB_Data.py`

## ▶️ Running the Server

Start the Flask server:

```bash
python app.py
```

The server will run at:
```
http://localhost:5001
```

## 🔄 Basic Workflow

### 👨‍🏫 Teacher Workflow

1. **Create Account** - Register as a teacher
2. **Login** - Authenticate using credentials
3. **Start Session** - Create a new attendance session (generates unique session code)
4. **Manage Session** - Lock/unlock session as needed
5. **End Session** - Stop the attendance session
6. **Export Data** - Download attendance records

### 👨‍🎓 Student Workflow

1. **Create Account** - Register as a student
2. **Upload Face** - Submit face image for recognition
3. **Join Session** - Enter session code to join active session
4. **Auto-Attendance** - System verifies face and marks attendance automatically

## 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/teacher/signup` | Teacher registration |
| `/teacher/login` | Teacher login (returns JWT) |
| `/student/signup` | Student registration |
| `/student/login` | Student login (returns JWT) |
| `/student/upload-face` | Upload student face image |
| `/session/start` | Start new attendance session |
| `/session/lock` | Lock active session |
| `/session/unlock` | Unlock locked session |
| `/session/stop` | Stop active session |
| `/session/mark` | Mark attendance using face recognition |
| `/session/attendance` | Fetch attendance list for session |

> **Note**: Exact route names may vary based on your implementation.

## 📷 Face Recognition Flow

1. **Registration Phase**
   - Student uploads face image
   - System generates embedding using `get_embedding_from_bytes()`
   - Embedding stored in MySQL database

2. **Attendance Marking Phase**
   - Student submits image during active session
   - New embedding generated from submitted image
   - System calculates distance between stored and new embeddings
   - If distance < threshold → Student marked **Present**
   - If distance > threshold → Recognition failed

## 🔒 Security Considerations

- All passwords should be hashed before storage
- JWT tokens expire after a set duration
- Session codes are unique and time-limited
- Face embeddings are stored securely in the database
- File uploads are validated and sanitized

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


**Built with ❤️ using Flask and Face Recognition**
