# Automated-Attendance-System-using-Face-Recognition-QR-Verification

To make the attendance system working, we began thinking what we can do so that the student in the classroom
can instantly mark their attendance without having to say “Present Mam/Sir”. To solve this problem, we are going
to use some ML (Machine Learning) model that can detect the face of the student with the data provided by the
student during registration.
In this project, we have a teacher and student portal. Through these portals, student can view their attendance
details, while teacher can see the details of the student. In the teacher portal, a button is provided that allow teacher
to generate a QR code for a limited amount of time. On student portal a notification will appear when attendance
marking has started. Student have to click the icon saying mark attendance in the student portal to Mark
Attendance after clicking the icon the camera will automatically open in the student device through which student
can scan the QR code after successfully scanning, then their front camera captures a photo. This photo is sent to a
python script, which uses the pre-trained ML model to match the student face with the provided data (at the time of
registration), if the photo is matched then the attendance is marked “Present”. The marked student details such as
student name, student ID, and the exact time of marking are automatically added to the attendance file.
This is the basic flow of our project that are we going to implement.
