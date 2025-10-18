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







We have upgraded some of the part of our system like we have now added button where teacher  can see students live attendance in their respective dashboard and we added new feature like lock session when teacher start a session he/she can lock that particular session so that no  extra student can join the lecture meaning student can’t mark themselves present when they are not present inside the class and instead of using the .pkl file to save embedding we are using json file to  save the student face embedding and we are using different formula to calculate to measure to check the similarity between the two facial encoding (One that was stored during registration  and second was when student start taking attendance)or not at first we were using the cosine similarity and now we are using Euclidean distance to calculate the similarity between two facial encoding  these are some of the feature we are current added in our project . 

Moule/Liabraries  Used:
Module Name	Used for/Purpose	Status
Mysql.connector	Connecting database	completed
json	To store embedding of images	completed
csv	Convert attendance data into csv file	completed
os	Create Directory for storing (face data)	completed
numpy	Use in getting result of Euclidean distance.	completed
Facenet_pytorch(torch)	Use to access module like MTCNN,InceptionResnetV1	completed
MTCNN	Crop the image	completed
InceptionResnetV1	To get the embedding of the image	completed
qrcode	Use to create QR code that is generated when teacher start their session	completed
django	To create UI	Not complete
Flask (Flask,jsonify, request)	Use to connect the front-end with backend	Not complete

