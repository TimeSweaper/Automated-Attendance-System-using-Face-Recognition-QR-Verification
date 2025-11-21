import os
import time
import shutil
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

import jwt
import logging

from flask_socketio import SocketIO, join_room, leave_room

from Database.DB_Data import create_teacher, create_student, get_teacher_by_email, get_student_by_email,get_teacher_by_id, get_student_by_id,Start_Session, Lock_Session, Stop_Session, Mark_Attendance, get_Session_attendance,Export, get_all_students_with_embeddings, connectionTDB
from facerecog import get_embedding_from_bytes

PORT = int(os.getenv('PORT', 5001))  
JWT_SECRET = os.getenv('JWT_SECRET', 'AdityaAMS')
FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', '*')
UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'teachers'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'students'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, 'qrs'), exist_ok=True)

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app, origins=FRONTEND_ORIGIN, supports_credentials=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
app.config['SECRET_KEY'] = JWT_SECRET

socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("attendance_app")

def generate_token(user_id, expires_minutes=60*24):
    payload = {'sub': user_id, 'exp': datetime.utcnow() + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload.get('sub')
    except Exception:
        return None

@app.route('/')
def index():
    return send_from_directory('static', 'login.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/face_data/<path:filename>')
def serve_face_data(filename):
    return send_from_directory('face_data', filename)


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if not (username and password and role):
        return jsonify({'error': 'username, password and role required'}), 400

    if role == 'teacher':
        user = get_teacher_by_email(username)
    else:
        user = get_student_by_email(username)

    if user is None:
        return jsonify({'error': 'Invalid username or role'}), 401
    if password != user.get('password_hash'):
        return jsonify({'error': 'Invalid password'}), 401

    token = generate_token(user['id'])
    return jsonify({'success': True, 'user': {'id': user['id'], 'name': user.get('name'), 'role': role, 'email': user.get('email')}, 'token': token})


@app.route('/api/register/teacher', methods=['POST'])
def api_register_teacher():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    department = request.form.get('department')
    if not (name and email and password):
        return jsonify({'error': 'name, email, password required'}), 400

    photo = request.files.get('photo')
    photo_path = None
    if photo:
        filename = secure_filename(photo.filename or 'teacher.jpg')
        save_path = os.path.join(UPLOAD_DIR, 'teachers', f"{int(time.time())}_{filename}")
        photo.save(save_path)
        photo_path = os.path.relpath(save_path, start='.')
        photo_path = photo_path.replace("\\", "/")

    try:
        new_id = create_teacher(name=name, teacher_id=None, email=email, password_hash=password, department=department, photo_path=photo_path)
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        app.logger.exception("DB error (create_teacher)")
        return jsonify({'error': str(e)}), 500


import os, shutil
from werkzeug.utils import secure_filename
from flask import jsonify, request

@app.route('/api/register/student', methods=['POST'])
def api_register_student():
    name = request.form.get('name')
    student_id = request.form.get('student_id')
    email = request.form.get('email')
    password = request.form.get('password')
    course = request.form.get('course')
    subjects = request.form.get('subjects')
    photo = request.files.get('photo')

    if not (name and email and password and photo):
        return jsonify({'error': 'name,email,password,photo required'}), 400

    students_dir = os.path.join(UPLOAD_DIR, 'students')
    os.makedirs(students_dir, exist_ok=True)

    raw_ext = os.path.splitext(secure_filename(photo.filename))[1] or '.jpg'
    raw_filename = secure_filename(f"{student_id}_front{raw_ext}")
    raw_save_path = os.path.join(students_dir, raw_filename)
    photo.save(raw_save_path)

    with open(raw_save_path, "rb") as f:
        img_bytes = f.read()

    aligned_path, embedding = get_embedding_from_bytes(
        img_bytes,
        studentID=student_id,
        studentName=name,
        save_files=True
    )

    if embedding is None:
        
        return jsonify({'error': 'no face detected in photo'}), 400

    try:
        back_ext = os.path.splitext(aligned_path)[1] if aligned_path else raw_ext
        back_filename = secure_filename(f"{student_id}_back{back_ext}")
        back_save_path = os.path.join(students_dir, back_filename)

        if aligned_path and os.path.exists(aligned_path):
            shutil.copyfile(aligned_path, back_save_path)
        else:
            shutil.copyfile(raw_save_path, back_save_path)

        
        rel_front_path = os.path.relpath(raw_save_path, start='.').replace("\\", "/")
        rel_back_path = os.path.relpath(back_save_path, start='.').replace("\\", "/")

        new_id = create_student(
            name=name,
            student_id=student_id,
            email=email,
            password_hash=password,
            photo_path=rel_front_path,       
            photo_back_path=rel_back_path,   
            department=None,
            course=course,
            subjects=subjects,
            face_encoding={'embedding': embedding, 'model': 'InceptionResnetV1_vggface2'}
        )

        return jsonify({
            'success': True,
            'id': new_id,
            'photo_front': rel_front_path,
            'photo_back': rel_back_path
        })
    except Exception as e:
        app.logger.exception("DB error (create_student)")
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/start', methods=['POST'])
def api_start_session():
    data = request.get_json() or {}
    teacher_email = data.get('teacher_email')
    subject = data.get('subject')
    section = data.get('section')
    app.logger.info("api_start_session payload: %s", data)
    teacher = get_teacher_by_email(teacher_email)
    app.logger.info("get_teacher_by_email(%s) -> %s", teacher_email, str(bool(teacher)))
    if not teacher:
        return jsonify({'error': 'teacher not found'}), 404

    info = Start_Session(teacherId=teacher['id'], subject=subject, section=section, code=data.get('code'))
    qr_path = None
    try:
        import qrcode
        sid = info['id']
        img = qrcode.make(str(sid))
        qr_dir = os.path.join(UPLOAD_DIR, 'qrs'); os.makedirs(qr_dir, exist_ok=True)
        qr_path_full = os.path.join(qr_dir, f"qr_session_{sid}.png")
        img.save(qr_path_full)
        qr_path = os.path.relpath(qr_path_full, start='.').replace("\\", "/")
    except Exception:
        qr_path = None

    return jsonify({'success': True, 'session': info, 'qr': qr_path})

@app.route('/api/session/lock', methods=['POST'])
def api_lock_session():
    data = request.get_json() or {}
    sid = data.get('session_id')
    if not sid:
        return jsonify({'error': 'session_id required'}), 400
    Lock_Session(int(sid))
    socketio.emit('session_locked', {'session_id': int(sid)}, room=f"session_{int(sid)}")
    return jsonify({'success': True})

@app.route('/api/session/stop', methods=['POST'])
def api_stop_session():
    data = request.get_json() or {}
    sid = data.get('session_id')
    if not sid:
        return jsonify({'error': 'session_id required'}), 400
    Stop_Session(int(sid))
    socketio.emit('session_stopped', {'session_id': int(sid)}, room=f"session_{int(sid)}")
    return jsonify({'success': True})


def l2_distance(live_embed, stored_embed):
    total = 0.0
    n = min(len(live_embed), len(stored_embed))
    for i in range(n):
        da = float(live_embed[i]); db = float(stored_embed[i])
        diff = da - db
        total += diff * diff
    return total ** 0.5

@app.route('/api/attendance/mark-face', methods=['POST'])
def api_mark_face():
    session_id = request.form.get('session_id')
    photo = request.files.get('photo')
    if not (session_id and photo):
        return jsonify({'error': 'session_id and photo required'}), 400

    img_bytes = photo.read()
    aligned_path, live_embed = get_embedding_from_bytes(img_bytes, save_files=False)
    if live_embed is None:
        return jsonify({'success': False, 'reason': 'no-face'})

    students = get_all_students_with_embeddings()
    best = None; best_dist = float('inf')
    for s in students:
        stored = s.get('face_encoding')
        if not stored:
            continue
        if isinstance(stored, dict) and 'embedding' in stored:
            stored_embed = stored['embedding']
        else:
            stored_embed = stored
        if not stored_embed:
            continue
        dist = l2_distance(live_embed, stored_embed)
        if dist < best_dist:
            best_dist = dist; best = s

    threshold = float(request.form.get('threshold', 1.0))
    if best is None or best_dist > threshold:
        return jsonify({'success': False, 'reason': 'no-match', 'best_dist': best_dist})

    try:
        res = Mark_Attendance(sessionId=int(session_id), studentId=int(best['id']), status="Present", method="face", device_info="webupload")
        if res.get('ok', False):
            teacher_room = f"session_{int(session_id)}"
            payload = {
                "session_id": int(session_id),
                "student": {
                    "id": best['id'],
                    "name": best['name'],
                    "email": best.get('email')
                },
                "status": "Present",
                "method": "face"
            }
            socketio.emit('attendance_marked', payload, room=teacher_room)

            try:
                updated_summary = compute_attendance_summary(int(best['id']))
                student_room = f"student_{int(best['id'])}"
                socketio.emit('attendance_summary_updated', {'student_id': int(best['id']), 'summary': updated_summary}, room=student_room)
            except Exception:
                app.logger.exception("Failed to compute/emit student summary")

        return jsonify({'success': True, 'student': {'id': best['id'], 'name': best['name']}, 'dist': best_dist, 'mark_result': res})
    except Exception as e:
        app.logger.exception("DB error on mark")
        return jsonify({'error': str(e)}), 500


def compute_attendance_summary(student_id):
    conn = None; cur = None
    try:
        conn = connectionTDB()
        cur = conn.cursor(dictionary=True)
        sql = """
            SELECT s.subject AS subject,
                   COUNT(DISTINCT s.id) AS total_sessions,
                   SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count
            FROM session s
            LEFT JOIN attendance a ON a.sessionID = s.id AND a.studentID = %s
            GROUP BY s.subject
            HAVING total_sessions > 0
        """
        cur.execute(sql, (student_id,))
        rows = cur.fetchall()

        subjects = []
        overall_present = 0
        overall_total = 0
        for r in rows:
            present = int(r['present_count'] or 0)
            total = int(r['total_sessions'] or 0)
            pct = round((present / total) * 100, 2) if total > 0 else 0.0
            subjects.append({"subject": r['subject'], "present": present, "total": total, "percentage": pct})
            overall_present += present
            overall_total += total

        subjects = sorted(subjects, key=lambda x: x['percentage'])  # worst-first
        overall_pct = round((overall_present / overall_total) * 100, 2) if overall_total > 0 else 0.0
        return {"student_id": student_id, "overall": {"present": overall_present, "total": overall_total, "percentage": overall_pct}, "subjects": subjects}
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/api/student/me/attendance/summary', methods=['GET'])
def api_student_attendance_summary():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({'error': 'student_id required (or implement auth)'}), 400
    try:
        sid = int(student_id)
    except:
        return jsonify({'error': 'invalid student_id'}), 400
    try:
        summary = compute_attendance_summary(sid)
        return jsonify(summary)
    except Exception as e:
        app.logger.exception("Error computing summary")
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/attendance/<int:session_id>', methods=['GET'])
def api_get_session_attendance(session_id):
    try:
        rows = get_Session_attendance(session_id)
        return jsonify({'success': True, 'attendance': rows})
    except Exception as e:
        app.logger.exception("Error fetching session attendance")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/export/<int:session_id>', methods=['GET'])
def api_export_session(session_id):
    out_path = f"attendance_session_{session_id}.csv"
    try:
        ok = Export(session_id, out_path)
        if not ok:
            return jsonify({'error': 'export_failed'}), 500
        return send_file(out_path, mimetype='text/csv', as_attachment=True, download_name=out_path)
    except Exception as e:
        app.logger.exception("Export error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/teacher/<int:teacher_id>', methods=['GET'])
def api_get_teacher(teacher_id):
    try:
        t = get_teacher_by_id(teacher_id)
        if t is None:
            return jsonify({'error': 'teacher_not_found'}), 404
        t.pop('password_hash', None)
        return jsonify({'success': True, 'teacher': t})
    except Exception as e:
        app.logger.exception("Error in api_get_teacher")
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/<int:student_id>', methods=['GET'])
def api_get_student(student_id):
    try:
        s = get_student_by_id(student_id)
        if s is None:
            return jsonify({'error': 'student_not_found'}), 404
        s.pop('password_hash', None)
        return jsonify({'success': True, 'student': s})
    except Exception as e:
        app.logger.exception("Error in api_get_student")
        return jsonify({'error': str(e)}), 500
@app.route('/api/student/<int:student_id>/upload-photo', methods=['POST'])
def api_update_student_photo(student_id):
    photo = request.files.get('photo')
    
    if not photo:
        return jsonify({'error': 'photo required'}), 400
    
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'student not found'}), 404
    
    students_dir = os.path.join(UPLOAD_DIR, 'students')
    os.makedirs(students_dir, exist_ok=True)
    
    raw_ext = os.path.splitext(secure_filename(photo.filename))[1] or '.jpg'
    raw_filename = secure_filename(f"{student.get('student_id', student_id)}_front{raw_ext}")
    raw_save_path = os.path.join(students_dir, raw_filename)
    photo.save(raw_save_path)
    
    with open(raw_save_path, "rb") as f:
        img_bytes = f.read()
    
    aligned_path, embedding = get_embedding_from_bytes(
        img_bytes,
        studentID=student.get('student_id', str(student_id)),
        studentName=student.get('name', 'Student'),
        save_files=True
    )
    
    if embedding is None:
        if os.path.exists(raw_save_path):
            os.remove(raw_save_path)
        return jsonify({'error': 'no face detected in photo'}), 400
    
    try:
        back_ext = os.path.splitext(aligned_path)[1] if aligned_path else raw_ext
        back_filename = secure_filename(f"{student.get('student_id', student_id)}_back{back_ext}")
        back_save_path = os.path.join(students_dir, back_filename)
        
        if aligned_path and os.path.exists(aligned_path):
            shutil.copyfile(aligned_path, back_save_path)
        else:
            shutil.copyfile(raw_save_path, back_save_path)
        
        rel_front_path = os.path.relpath(raw_save_path, start='.').replace("\\", "/")
        rel_back_path = os.path.relpath(back_save_path, start='.').replace("\\", "/")
        
        from Database.DB_Data import update_student_photo
        
        face_encoding_dict = {
            'embedding': embedding,
            'model': 'InceptionResnetV1_vggface2'
        }
        
        update_student_photo(
            student_id=student_id,
            photo_path=rel_front_path,
            photo_back_path=rel_back_path,
            face_encoding=face_encoding_dict
        )
        
        return jsonify({
            'success': True,
            'message': 'Photo updated successfully',
            'photo_path': rel_front_path,
            'photo_back_path': rel_back_path
        })
        
    except Exception as e:
        app.logger.exception("Error updating student photo")
        return jsonify({'error': str(e)}), 500


@socketio.on('join_session')
def on_join_session(data):
    sid = data.get('session_id')
    if sid:
        room = f"session_{sid}"
        join_room(room)
        try:
            rows = get_Session_attendance(int(sid))
            socketio.emit('attendance_snapshot', {'session_id': int(sid), 'attendance': rows}, room=request.sid)
        except Exception:
            pass

@socketio.on('leave_session')
def on_leave_session(data):
    sid = data.get('session_id')
    if sid:
        leave_room(f"session_{sid}")

@socketio.on('join_student_room')
def on_join_student(data):
    sid = data.get('student_id')
    if sid:
        room = f"student_{sid}"
        join_room(room)
        try:
            summary = compute_attendance_summary(int(sid))
            socketio.emit('attendance_summary_updated', {'student_id': int(sid), 'summary': summary}, room=request.sid)
        except Exception:
            pass

@socketio.on('leave_student_room')
def on_leave_student(data):
    sid = data.get('student_id')
    if sid:
        leave_room(f"student_{sid}")

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=PORT, debug=False)
