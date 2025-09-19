# init_data.py - FIXED VERSION
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, UserRole, Department, Faculty, Subject, SubjectSession, SessionType, Room, RoomType, Batch
from models import hash_password, init_db

def initialize_sample_data():
    # Initialize database
    session = init_db()
    
    try:
        # Check if data already exists
        existing_users = session.query(User).count()
        if existing_users > 0:
            print("Data already exists. Skipping initialization.")
            return
        
        print("Initializing sample data...")
        
        # Create default admin user
        admin_user = User(
            username="admin",
            password_hash=hash_password("admin123"),
            email="admin@care.edu",
            role=UserRole.ADMIN,
            full_name="System Administrator"
        )
        session.add(admin_user)
        session.flush()
        
        # Create ECE department
        ece_department = Department(
            code="ECE",
            name="Electronics and Communication Engineering",
            hod_id=None
        )
        session.add(ece_department)
        session.flush()
        
        # Create HOD user
        hod_user = User(
            username="hod_ece",
            password_hash=hash_password("hod123"),
            email="hod.ece@care.edu",
            role=UserRole.HOD,
            full_name="ECE HOD"
        )
        session.add(hod_user)
        session.flush()
        
        hod_faculty = Faculty(
            user_id=hod_user.id,
            employee_id="HOD001",
            max_weekly_load=3,
            avg_leaves_per_month=1.0,
            qualifications="Ph.D in Electronics",
            specialization="Communication Systems"
        )
        session.add(hod_faculty)
        session.flush()
        
        # Update department with HOD
        ece_department.hod_id = hod_faculty.id
        
        # Create timetable officer
        officer_user = User(
            username="timetable_officer",
            password_hash=hash_password("officer123"),
            email="timetable@care.edu",
            role=UserRole.TIMETABLE_OFFICER,
            full_name="Timetable Officer"
        )
        session.add(officer_user)
        session.flush()
        
        # Create faculty users
        faculty_data = [
            ("asra", "Ms. H. Asra Jabeen", "EMF", "FAC001"),
            ("rubitha", "Ms. K. Rubitha", "Signals and Systems", "FAC002"),
            ("shantha", "Ms. B. ShanthaSheela", "EDC", "FAC003"),
            ("shiva", "Mrs. M. Shiva Shankari", "DSD", "FAC004"),
            ("christina", "Ms. Christina Merline", "Probability", "FAC005")
        ]
        
        faculty_objects = []
        for username, full_name, specialization, emp_id in faculty_data:
            user = User(
                username=username,
                password_hash=hash_password("faculty123"),
                email=f"{username}@care.edu",
                role=UserRole.FACULTY,
                full_name=full_name
            )
            session.add(user)
            session.flush()
            
            faculty = Faculty(
                user_id=user.id,
                employee_id=emp_id,
                max_weekly_load=5,
                avg_leaves_per_month=2.0,
                qualifications="M.Tech",
                specialization=specialization
            )
            session.add(faculty)
            faculty_objects.append(faculty)
            session.flush()
        
        # Create ECE batch
        ece_batch = Batch(
            department_id=ece_department.id,
            year=2,
            semester=3,
            section="A",
            strength=60
        )
        session.add(ece_batch)
        session.flush()
        
        # Create subjects based on your timetable
        subjects_data = [
            ("U24EC311", "Electromagnetic Fields", 4, 6),
            ("U24EC323", "Signals and Systems", 4, 10),
            ("U24EC333", "Electronics Devices and Circuits", 4, 10),
            ("U24EC343", "Digital System Design", 4, 10),
            ("U24MA331", "Probability and Random Process", 4, 7),
            ("APTITUDE", "Aptitude & Communication Skill", 1, 1),
            ("LIBRARY", "Library/Counseling", 1, 1)
        ]
        
        subject_objects = []
        for code, name, credits, total_hours in subjects_data:
            subject = Subject(
                code=code,
                name=name,
                credits=credits,
                total_hours=total_hours
            )
            session.add(subject)
            subject_objects.append(subject)
            session.flush()
        
        # Create subject sessions
        for subject in subject_objects:
            if subject.code in ["U24EC323", "U24EC333", "U24EC343"]:
                # Add theory and lab sessions for lab subjects
                theory_session = SubjectSession(
                    subject_id=subject.id,
                    session_type=SessionType.THEORY,
                    duration_hours=1.0,
                    weekly_frequency=3,
                    requires_lab=False
                )
                session.add(theory_session)
                
                lab_session = SubjectSession(
                    subject_id=subject.id,
                    session_type=SessionType.LAB,
                    duration_hours=2.0,
                    weekly_frequency=2,
                    requires_lab=True,
                    min_days_after_theory=1
                )
                session.add(lab_session)
            else:
                # Regular theory subjects
                session_count = subject.total_hours
                theory_session = SubjectSession(
                    subject_id=subject.id,
                    session_type=SessionType.THEORY,
                    duration_hours=1.0,
                    weekly_frequency=session_count,
                    requires_lab=False
                )
                session.add(theory_session)
        
        # Create rooms
        rooms_data = [
            ("ECE-101", "ECE Theory Room", RoomType.THEORY_ROOM, 60, ece_department.id),
            ("ECE-LAB", "ECE Laboratory", RoomType.LAB_ROOM, 30, ece_department.id),
            ("COMMON-HALL", "Common Hall", RoomType.COMMON_HALL, 100, None),
            ("SEMINAR-1", "Seminar Hall 1", RoomType.SEMINAR_HALL, 80, None)
        ]
        
        for code, name, room_type, capacity, dept_id in rooms_data:
            room = Room(
                code=code,
                name=name,
                room_type=room_type,
                capacity=capacity,
                department_id=dept_id,
                is_available=True
            )
            session.add(room)
        
        # Commit all changes
        session.commit()
        print("✅ Sample data initialized successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error initializing data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    initialize_sample_data()