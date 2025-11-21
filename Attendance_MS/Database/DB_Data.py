import json
import csv
import mysql.connector
from Database.DB_Conn import dbHost, dbName, dbPass, dbPort, dbUser

def connectionTDB():
    """Return a new MySQL connection (caller should close)."""
    connection = mysql.connector.connect(
        host=dbHost, port=dbPort, user=dbUser, password=dbPass, database=dbName
    )
    return connection


def create_teacher(name, teacher_id, email, password_hash, department=None, photo_path=None):
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        sql = """INSERT INTO teachers (teacher_id, name, email, password_hash, department, photo_path)
                 VALUES (%s,%s,%s,%s,%s,%s)"""
        cur.execute(sql, (teacher_id, name, email, password_hash, department, photo_path))
        conn.commit()
        return cur.lastrowid
    except Exception:
        if conn: conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()


def create_student(name, student_id, email, password_hash, photo_path=None, photo_back_path=None, department=None, course=None, subjects=None, face_encoding=None):
    """Create a new student with both front and back photo paths."""
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        sql = """INSERT INTO students (student_id, name, email, password_hash, department, course, subjects, photo_path, photo_back_path, face_encoding)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(sql, (student_id, name, email, password_hash, department, course, subjects, photo_path, photo_back_path, json.dumps(face_encoding) if face_encoding else None))
        conn.commit()
        return cur.lastrowid
    except Exception:
        if conn: conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_teacher_by_email(email):
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        sql = "SELECT id, teacher_id, name, email, password_hash, department, photo_path FROM teachers WHERE email=%s"
        cur.execute(sql, (email,))
        row = cur.fetchone()
        if not row: return None
        return {"id": row[0], "teacher_id": row[1], "name": row[2], "email": row[3], "password_hash": row[4], "department": row[5], "photo_path": row[6]}
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_student_by_email(email):
    """Get student by email with both photo paths."""
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        sql = "SELECT id, student_id, name, email, password_hash, department, course, subjects, photo_path, photo_back_path, face_encoding FROM students WHERE email=%s"
        cur.execute(sql, (email,))
        row = cur.fetchone()
        if not row: return None
        return {
            "id": row[0], 
            "student_id": row[1], 
            "name": row[2], 
            "email": row[3],
            "password_hash": row[4], 
            "department": row[5], 
            "course": row[6],
            "subjects": row[7], 
            "photo_path": row[8],
            "photo_back_path": row[9],
            "face_encoding": json.loads(row[10]) if row[10] else None
        }
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_all_students_with_embeddings():
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        cur.execute("SELECT id, name, email, face_encoding FROM students WHERE face_encoding IS NOT NULL")
        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({"id": r[0], "name": r[1], "email": r[2], "face_encoding": json.loads(r[3]) if r[3] else None})
        return out
    finally:
        if cur: cur.close()
        if conn: conn.close()



def Start_Session(teacherId, subject=None, section=None, code=None):
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        if code is None:
            code = "S" + str(teacherId) + str(int(__import__('time').time()))
        sql = "INSERT INTO session (teacher_id, code, subject, section, locked) VALUES (%s,%s,%s,%s,0)"
        cur.execute(sql, (teacherId, code, subject, section))
        conn.commit()
        new_id = cur.lastrowid
        cur.execute("SELECT id, code, subject, section, started_at, locked, ended_at FROM session WHERE id=%s", (new_id,))
        row = cur.fetchone()
        return {"id": row[0], "code": row[1], "subject": row[2], "section": row[3], "started_at": row[4], "locked": row[5], "ended_at": row[6]}
    except Exception:
        if conn: conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

def Lock_Session(sessionId):
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        cur.execute("UPDATE session SET locked=1 WHERE id=%s", (sessionId,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def Stop_Session(sessionId):
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        cur.execute("UPDATE session SET locked=1, ended_at=NOW() WHERE id=%s", (sessionId,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def Mark_Attendance(sessionId, studentId, status="Present", method="qr_face", device_info=None):
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        cur.execute("SELECT locked FROM session WHERE id=%s", (sessionId,))
        row = cur.fetchone()
        if row is None:
            return {"ok": False, "reason": "session_not_found"}
        if row[0] == 1:
            return {"ok": False, "reason": "session_locked"}
        cur.execute("INSERT INTO attendance (sessionID, studentID, status, method, device_info) VALUES (%s,%s,%s,%s,%s)",
                    (sessionId, studentId, status, method, device_info))
        conn.commit()
        return {"ok": True, "already": False}
    except mysql.connector.IntegrityError as e:
        if hasattr(e, "errno") and e.errno == 1062:
            return {"ok": True, "already": True}
        else:
            if conn: conn.rollback()
            raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_Session_attendance(sessionId):
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        sql = """SELECT a.id, a.marked_at, a.status, a.method, u.name, u.email
                 FROM attendance a JOIN students u ON u.id = a.studentID
                 WHERE a.sessionID = %s ORDER BY a.id DESC"""
        cur.execute(sql, (sessionId,))
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({"id": row[0], "marked_at": row[1], "status": row[2], "method": row[3], "name": row[4], "email": row[5]})
        return result
    finally:
        if cur: cur.close()
        if conn: conn.close()

def Export(sessionID, outPath):
    conn = None; cur = None; file = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        sql = """SELECT a.id, a.marked_at, a.status, a.method, u.name, u.email
                 FROM attendance a JOIN students u ON u.id = a.studentID
                 WHERE a.sessionID = %s ORDER BY a.id ASC"""
        cur.execute(sql, (sessionID,))
        rows = cur.fetchall()
        file = open(outPath, "w", newline="", encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(["SessionID", "StudentName", "Email", "Status", "Method", "MarkedAT"])
        for row in rows:
            writer.writerow([sessionID, row[4], row[5], row[2], row[3], str(row[1])])
        return True
    except Exception:
        if conn: conn.rollback()
        raise
    finally:
        if file: file.close()
        if cur: cur.close()
        if conn: conn.close()


def get_teacher_by_id(tid):
    """Return teacher dict by numeric id, or None."""
    connection = None
    cursor = None
    try:
        connection = connectionTDB()
        cursor = connection.cursor()
        sql = ("SELECT id, teacher_id, name, email, password_hash, department, photo_path, created_at "
               "FROM teachers WHERE id = %s")
        cursor.execute(sql, (tid,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "teacher_id": row[1],
            "name": row[2],
            "email": row[3],
            "password_hash": row[4],
            "department": row[5],
            "photo_path": row[6],
            "created_at": row[7]
        }
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def get_student_by_id(sid):
    """Return student dict by numeric id with both photo paths, or None."""
    connection = None
    cursor = None
    try:
        connection = connectionTDB()
        cursor = connection.cursor()
        sql = ("SELECT id, student_id, name, email, password_hash, department, course, subjects, "
               "photo_path, photo_back_path, face_encoding, created_at "
               "FROM students WHERE id = %s")
        cursor.execute(sql, (sid,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "student_id": row[1],
            "name": row[2],
            "email": row[3],
            "password_hash": row[4],
            "department": row[5],
            "course": row[6],
            "subjects": row[7],
            "photo_path": row[8],         
            "photo_back_path": row[9],    
            "face_encoding": json.loads(row[10]) if row[10] else None,
            "created_at": row[11]
        }
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
        
def update_student_photo(student_id, photo_path, photo_back_path, face_encoding):
    """Update student photo paths and face encoding."""
    conn = None; cur = None
    try:
        conn = connectionTDB(); cur = conn.cursor()
        sql = """UPDATE students 
                 SET photo_path = %s, 
                     photo_back_path = %s,
                     face_encoding = %s
                 WHERE id = %s"""
        cur.execute(sql, (
            photo_path, 
            photo_back_path, 
            json.dumps(face_encoding) if face_encoding else None,
            student_id
        ))
        conn.commit()
        return True
    except Exception:
        if conn: conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()
