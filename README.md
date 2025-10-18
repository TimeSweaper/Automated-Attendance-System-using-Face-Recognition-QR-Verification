#  Automated Attendance System using Face Recognition & QR Verification

## 📋 Overview
The **Automated Attendance System** is designed to modernize traditional attendance methods by leveraging **facial recognition** and **QR verification**.  
This system allows teachers to start an attendance session by generating a **unique QR code**, while students can mark their attendance by scanning it.  
After scanning, the student’s **face is captured and verified** using machine learning models to ensure authenticity — preventing proxy attendance and duplicate marking.

---

##  Key Features
- 👨‍🏫 **Teacher Dashboard:**  
  - View real-time student attendance.  
  - Start/stop attendance sessions.  
  - Lock sessions to prevent late entries.  

- 🧑‍🎓 **Student Portal:**  
  - Receive live notifications when attendance begins.  
  - Scan QR code and automatically mark attendance through face detection.  
  - View personal attendance history.

- 🔐 **Security Enhancements:**  
  - Session locking to prevent multiple attendance attempts.  
  - Euclidean distance–based face similarity check.  
  - Database constraints to prevent duplicate records.  

- 🧠 **Machine Learning Integration:**  
  - Uses `MTCNN` for face detection.  
  - Uses `InceptionResNetV1` for feature extraction (face embedding).  
  - Compares embeddings using **Euclidean** or **Cosine Similarity**.  

---

## 🧩 Modules / Libraries Used

| Module Name | Purpose / Usage | Status |
|--------------|----------------|--------|
| `mysql.connector` | Connect to MySQL database | ✅ Completed |
| `json` | Store embedding of images | ✅ Completed |
| `csv` | Export attendance data | ✅ Completed |
| `os` | Directory creation for face data | ✅ Completed |
| `numpy` | Perform Euclidean distance calculations | ✅ Completed |
| `facenet_pytorch` | Access ML models (`MTCNN`, `InceptionResNetV1`) | ✅ Completed |
| `MTCNN` | Crop the detected face | ✅ Completed |
| `InceptionResNetV1` | Generate face embeddings | ✅ Completed |
| `qrcode` | Generate unique QR codes per session | ✅ Completed |
| `django` | Create full web-based UI | 🔄 In Progress |
| `flask` | Temporary frontend-backend connection (testing) | 🔄 In Progress |

---
## 🧮 Working Principle
1. **Teacher Login:**  
   The teacher starts a class session and generates a QR code valid for a short time.

2. **Student Action:**  
   Students log into their portal, scan the displayed QR code, and the system activates their webcam.

3. **Face Recognition:**  
   The captured image is compared with stored facial embeddings from registration using **Euclidean distance**.

4. **Attendance Marking:**  
   If similarity is above the threshold, the student’s attendance is marked as *Present* with timestamp, student ID, and name.

5. **Data Storage:**  
   Attendance details are saved in a **MySQL database** and can be exported to `.csv` for record-keeping.

---

## 📦 Project Deliverables
- Django-based **web application** for teachers and students.  
- Real-time **face recognition attendance marking**.  
- Secure **QR-based verification system**.  
- **Admin dashboard** for managing users and reports.  
- Complete **documentation, database schema, and user guide**.

---

## 🛠️ Tools & Technologies
- **Languages:** Python, HTML, CSS, JavaScript  
- **Frameworks:** Django, Flask  
- **Libraries:** OpenCV, NumPy, FaceNet-PyTorch, MTCNN, qrcode  
- **Database:** MySQL  
- **IDE:** Visual Studio Code
- **Jupyter Notebook:** For testing and checking if Euclidean distance work effectively or not  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/Automated-Attendance-System.git
cd Automated-Attendance-System
