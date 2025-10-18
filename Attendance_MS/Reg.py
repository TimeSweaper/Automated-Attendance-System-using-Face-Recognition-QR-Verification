import random
from Database.DB_Data import User_detail, User_Email, Start_Session, Mark_Attendance, Export, Lock_Session, Stop_Session
from faceRecog import capture_embed, CaptureImage
import json
import cv2
import time
import qrcode




def RandomCod(length):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUV0123456789abcdefghijklmnopqrstuvqxyz"
    code = ""
    index = 0
    while index < length:
        pos = random.randint(0, len(alphabet) - 1)
        ch = alphabet[pos]
        code = code + ch
        index = index + 1
    print(code)
    return code

code = RandomCod(7)

def GenerateQRForSession(info):

    sid = info["id"]

    data = sid
    path_qr = "qr_session_" + str(sid) + ".png"
    print(data)
    img = qrcode.make(data)
    img.save(path_qr)
    print("QR saved to:", path_qr)
    return path_qr,data



def ScanQRFromWebcam(timeout_seconds=20):
   

    cap = cv2.VideoCameraCapture = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open webcam for QR scan.")
        return None

    detector = cv2.QRCodeDetector()
    print("Aim the QR at the camera. Press Q to quit.")
    start = time.time()
    text = None

    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        data1, bbox, _ = detector.detectAndDecode(frame)
        if data1 is not None and data1 != "":
            text =  data1
            break
     
        
        cv2.putText(frame, "Scan QR Q to quit", (18, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("QR Scanner", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break

        if time.time() - start > timeout_seconds:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(data1)
    print(text)
    return text


def l2_distance(live_embed, stored_embed):
    total = 0.0
    i = 0
    n = len(live_embed)
    m = len(stored_embed)
    if n > m:
        n = m
    while i < n:
        da = float(live_embed[i])
        db = float(stored_embed[i])
        diff = da - db
        total = total + (diff * diff)
        i = i + 1
    x = total ** 0.5
    return x




def studentJoinByQR():
    print("---- STUDENT JOIN  ----")
    email = input("Student Email: ").strip()
    if email.isdigit() < 0:
        print("Incorrect Email.Pls Try again..")
        return    

    qr_text = ScanQRFromWebcam()
    if qr_text is None or qr_text.strip() == "":
        print("QR scan failed. Enter session id manually.")
        qr_text = input("Session ID (from teacher QR): ").strip()

    if qr_text.isdigit() is False:
        print("Invalid session id in QR/text.")
        return

    sessionID = int(qr_text)

    student = User_Email(email=email, role="student")
    if student is None:
        print("No student found with that email.")
        return

    if student.get("face_encoding") is None:
        print("No stored embedding for this student. Re-register the student.")
        return

    photo_path, live_embed = capture_embed(studentID=email, studentName=student["name"])
    if photo_path is None or live_embed is None:
        print("No face captured.")
        return

    try:
        stored_json = student["face_encoding"]
        data = json.loads(stored_json)
        if isinstance(data, dict) and "embedding" in data:
            stored_embed = data["embedding"]
        else:
            stored_embed = data
    except Exception as e:
        print("Could not read stored embedding:", str(e))
        return

    dist = l2_distance(live_embed, stored_embed)
    print("Match distance:", dist)

    threshold = 1.0
    if dist > threshold:
        print("Face did not match. Not marking attendance.")
        return

    result = Mark_Attendance(sessionId=sessionID, studentId=student["id"],status="Present", method="qr_face", device_info="Webcam")
    print("Mark result:", result)


def lockTeachSession():
    print("---- LOCK SESSION ----")
    sid = input("Enter session id: ").strip()
    if sid.isdigit() is False:
        print("Invalid id")
        return
    sid = int(sid)
    Lock_Session(sid)
    print("Session locked.")


def stopTeachSession():
    print("---- STOP SESSION ----")
    sid = input("Enter session id: ").strip()
    if sid.isdigit() is False:
        print("Invalid id")
        return
    sid = int(sid)
    Stop_Session(sid)
    print("Session stopped.")


def RegistrationStudent():
    print("---- REGISTRATION STUDENT ----")
    name = input("Student Name: ").strip()
    email = input("Student email: ").strip()
    course = input("Course: ").strip()
    subjets = input("Subjects: ").strip()
    password = input("Password: ").strip()

    photo_path, embedding = capture_embed(studentID=email, studentName=name)
    if photo_path is None or embedding is None:
        print("Registration Unsucessessfull")
        return None

    if course == "":
        course_save = None
    else:
        course_save = course

    if subjets == "":
        subjects_save = None
    else:
        subjects_save = subjets

    new_id = User_detail(role="student",name=name,email=email,password=password,photoPath=photo_path,department=None,course=course_save,subjects=subjects_save,faceEncodingList=embedding)
    print("Student Created Successfully with id:", new_id)
    return new_id


def TeacherRegistration(Temail=None):
    print("---- REGISTRATION TEACHER ----")
    name = input("Teacher name: ").strip()

    if Temail is None:
        email = input("Teacher Email: ").strip()
    else:
        email = Temail
        print("Using Email:", email)

    dept = input("Department: ").strip()
    password = input("Enter password: ").strip()

    photo_path = capture_embed(studentID=email, studentName=name)[0]
    if photo_path is None:
        print("Registration unsuccessfull")
        return None

    if dept == "":
        deptSave = None
    else:
        deptSave = dept

    teacherID = User_detail(role="teacher",name=name,email=email,password=password,photoPath=photo_path,department=deptSave)
    print("Teacher created ID:", teacherID)
    return teacherID


def TeacherVerify(email):
    teacher = User_Email(email, role="teacher")
    if teacher is not None:
        return teacher["id"]

    print("Teacher not found!")
    tid = TeacherRegistration(Temail=email)
    return tid


def startTeachSession():
    print("---- START SESSION ----")
    temail = input("Teacher Email: ")
    teacherID = TeacherVerify(temail)

    subject = input("Subject: ")
    section = input("Section: ")

    

    if subject == "":
        subjectCheck = None
        return
    else:
        subjectCheck = subject

    if section == "":
        sectionCheck = None
        return
    else:
        sectionCheck = section
    
    info = Start_Session(teacherId=teacherID, subject=subjectCheck, section=sectionCheck, code=code)
    print("Session Started:", info)
    GenerateQRForSession(info)

    return info


def exportCSV():
    print("--- EXPORT ATTENDANCE (CSV FILE) --- ")
    sid = input("Enter Session id: ")

    if sid.isdigit() is False:
        print("Invalid session id")
        return

    sid = int(sid)
    Dname = "attendance_session_" + str(sid) + ".csv"
    out_path = Dname

    try:
        ok = Export(sid, out_path)  
        if ok:
            print("Saved CSV to:", out_path)
        else:
            print("CSV file not saved")
    except Exception as e:
        print("Error while Saving CSV:", str(e))
