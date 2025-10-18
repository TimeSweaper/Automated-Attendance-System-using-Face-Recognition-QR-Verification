import mysql.connector
import json
import csv
from Database.DB_Conn import dbHost, dbName, dbPass,dbPort,dbUser

def connectionTDB():
        connection = mysql.connector.connect(host=dbHost,port=dbPort,user=dbUser,password=dbPass,database=dbName)
        return connection


def User_detail(role, name, email, password, photoPath,department=None, course=None, subjects=None, faceEncodingList=None):
    connection = None
    cursor = None

    try:
        if role != "teacher" and role != "student":
            raise ValueError("role must be teacher or student")

        if faceEncodingList is not None:
            faceJson = json.dumps(faceEncodingList)
        else:
            faceJson = None

        connection = connectionTDB()
        cursor = connection.cursor()

        sql = ""
        sql = sql + "INSERT INTO users "
        sql = sql + "(role, name, department, course, subjects, email, password_hash, photo_path, face_encoding) "
        sql = sql + "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        detail = (role,name,department,course,subjects,email,password,photoPath,faceJson)

        cursor.execute(sql, detail)
        connection.commit()
        new_id = cursor.lastrowid
        return new_id

    except Exception as e:
        if connection is not None:
            connection.rollback()
        raise e

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()



def User_Email(email, role=None):
    connection = None
    cursor = None
    try:
        connection = connectionTDB()
        cursor = connection.cursor()

        if role is None:
            sql = ""
            sql += "Select id, role, name, department, course, subjects, email, password_hash, photo_path, face_encoding, create_at, update_at "
            sql += "From users Where email=%s"
            detail = (email,)
        else:
            sql = ""
            sql += "Select id, role, name, department, course, subjects, email, password_hash, photo_path, face_encoding, create_at, update_at "
            sql += "From users Where email=%s and role=%s"
            detail = (email, role)

        cursor.execute(sql, detail)
        row = cursor.fetchone()
        if row is None:
            return None

        user = {}
        user["id"], user["role"] = row[0], row[1]
        user["name"], user["department"] = row[2], row[3]
        user["course"], user["subjects"] = row[4], row[5]
        user["email"], user["password_hash"] = row[6], row[7]
        user["photo_path"], user["face_encoding"] = row[8], row[9]
        user["create_at"], user["update_at"] = row[10], row[11]
        return user
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def Start_Session(teacherId, subject=None, section=None, code="ABSC1234"):
    connection = None
    cursor = None
    try:
        connection = connectionTDB()
        cursor = connection.cursor()

        sql = ""
        sql += "Insert Into session (teacher_id, code, subject, section, locked) "
        sql += "Values (%s,%s,%s,%s,0)"
        detail = (teacherId, code, subject, section)
        print(code)
        cursor.execute(sql, detail)
        connection.commit()  

        new_id = cursor.lastrowid

        sql2 = ""
        sql2 += "Select id, code, subject, section, started_at, locked, ended_at "
        sql2 += "From session Where id=%s"
        cursor.execute(sql2, (new_id,))
        row = cursor.fetchone()

        result = {}
        result["id"], result["code"] = row[0], row[1]
        result["subject"], result["section"] = row[2], row[3]
        result["started_at"], result["locked"] = row[4], row[5]
        result["ended_at"] = row[6]
        
        return result
    except Exception as e:
        if connection is not None:
            connection.rollback()
        raise e
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def Lock_Session(sessionId):
    connection = None
    cursor = None

    try:
        connection = connectionTDB()
        cursor = connection.cursor()

        sql = "Update session set locked=1 Where id=%s"
        detail = (sessionId,)

        cursor.execute(sql, detail)
        connection.commit()

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def Stop_Session(sessionId):
    connection = None
    cursor = None
    try:
        connection = connectionTDB()
        cursor = connection.cursor()
        sql = "Update session Set locked=1, ended_at=NOW() Where id=%s"
        cursor.execute(sql, (sessionId,))
        connection.commit()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def Mark_Attendance(sessionId, studentId, status="Present", method="qr_face", device_info=None):
    connection = None
    cursor = None

    try:
        connection = connectionTDB()
        cursor = connection.cursor()
        sql = "SELECT locked FROM session WHERE id=%s"
        detail = (sessionId,)
        cursor.execute(sql, detail)
        row = cursor.fetchone()
        if row is None:
            return {"ok": False, "reason": "session_not_found"}
        if row[0] == 1:
            return {"ok": False, "reason": "session_locked"}

        sql = ""
        sql = sql + "Insert into attendance (sessionID,studentID, status, method, device_info) "
        sql = sql + "values (%s,%s,%s,%s,%s)"
        detail = (sessionId, studentId, status, method, device_info)

        cursor.execute(sql, detail)
        connection.commit()

        result = {}
        result["ok"] = True
        result["already"] = False

        return result

    except mysql.connector.IntegrityError as e:
        if hasattr(e, "errno") and e.errno == 1062:
            result = {}
            result["ok"] = True
            result["already"] = True
            return result
        else:
            if connection is not None:
                connection.rollback()
            raise e

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()




def get_Session_attendance(sessionId):
    connection = None
    cursor = None
    try:
        connection = connectionTDB()
        cursor = connection.cursor()

        sql = ""
        sql += "Select a.id, a.marked_at, a.status, a.method, u.name, u.email "
        sql += "From attendance a "
        sql += "Join users u on u.id = a.studentID "
        sql += "Where a.sessionID = %s "
        sql += "Order by a.id desc"
        cursor.execute(sql, (sessionId,))
        rows = cursor.fetchall()

        result = []
        i = 0
        while i < len(rows):
            row = rows[i]
            item = {
                "id": row[0],
                "marked_at": row[1],
                "status": row[2],
                "method": row[3],
                "name": row[4],
                "email": row[5],
            }
            result.append(item)
            i += 1
        return result
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def Export(sessionID, outPath):
    connection = None
    cursor = None
    file = None

    try:
        connection = connectionTDB()
        cursor = connection.cursor()

        sql = ""
        sql = sql + "Select a.id, a.marked_at, a.status, a.method, u.name, u.email "
        sql = sql + "From attendance a "
        sql = sql + "Join users u on u.id = a.studentID "
        sql = sql + "Where a.sessionID = %s "
        sql = sql + "Order by a.id ASC"
        detail = (sessionID,)

        cursor.execute(sql, detail)
        rows = cursor.fetchall()

        file = open(outPath, "w", newline="", encoding="utf-8")
        writer = csv.writer(file)

        header = ["SessionID", "StudentName", "Email", "Status", "Method", "MarkedAT"]
        writer.writerow(header)

        i = 0
        while i < len(rows):
            row = rows[i]
            ID, marked_at = row[0], row[1]
            status, method = row[2], row[3]
            name, email = row[4], row[5]

            line = [sessionID, name, email, status, method, str(marked_at)]
            writer.writerow(line)

            i = i + 1

        return True

    except Exception as e:
        if connection is not None:
            connection.rollback()
        raise e

    finally:
        if file is not None:
            file.close()
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()