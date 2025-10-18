from Reg import RegistrationStudent,TeacherRegistration,startTeachSession,exportCSV
from Reg import lockTeachSession, stopTeachSession, studentJoinByQR

def main():
    print("--- ATTENDANCE MARKING SYSTEM ---")
    while(True):
        print("\n")
        print("1. Registration as Student","2. Registration as Teacher","3. Start Session","4. Export Attendance to CSV","5. Lock Session","6. Stop Session","7. Student Join by QR","8. Exit",sep='\n')
        

        choice = input("Enter choice: ")

        if choice == '1':
            RegistrationStudent()
        elif choice == '2':
            TeacherRegistration()
        elif choice == '3':
            info = startTeachSession()
            print("Save this session id: ",info["id"])
        elif choice == '4':
            exportCSV()
        elif choice == "5":
            lockTeachSession()
        elif choice == "6":
            stopTeachSession()
        elif choice == "7":
            studentJoinByQR()
        elif choice == "8":
            print("Goodbye.")
            
            break
        else:
            print("Invalid Choice")


if __name__ == "__main__":
    main()