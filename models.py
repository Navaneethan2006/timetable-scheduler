# models.py - FIXED VERSION
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
import json

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    TIMETABLE_OFFICER = "timetable_officer"
    HOD = "hod"
    FACULTY = "faculty"

class SessionType(enum.Enum):
    THEORY = "theory"
    LAB = "lab"
    TUTORIAL = "tutorial"
    SPECIAL = "special"

class RoomType(enum.Enum):
    THEORY_ROOM = "theory_room"
    LAB_ROOM = "lab_room"
    COMMON_HALL = "common_hall"
    SEMINAR_HALL = "seminar_hall"

class ApprovalStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    role = Column(Enum(UserRole), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Faculty(Base):
    __tablename__ = 'faculty'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    employee_id = Column(String(20), unique=True)
    max_weekly_load = Column(Integer, default=5)
    avg_leaves_per_month = Column(Float, default=2.0)
    qualifications = Column(String(200))
    specialization = Column(String(100))
    
    # Relationships
    user = relationship("User")
    subjects = relationship("FacultySubject", back_populates="faculty")

class FacultySubject(Base):
    __tablename__ = 'faculty_subjects'
    
    id = Column(Integer, primary_key=True)
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    is_primary = Column(Boolean, default=True)
    proficiency_level = Column(Integer, default=1)
    
    # Relationships
    faculty = relationship("Faculty", back_populates="subjects")
    subject = relationship("Subject", back_populates="faculty")

class FacultyUnavailability(Base):
    __tablename__ = 'faculty_unavailability'
    
    id = Column(Integer, primary_key=True)
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    day_of_week = Column(Integer)
    start_time = Column(String(8))
    end_time = Column(String(8))
    reason = Column(String(200))
    is_recurring = Column(Boolean, default=True)
    
    # Relationships
    faculty = relationship("Faculty")

class FacultyAlternate(Base):
    __tablename__ = 'faculty_alternates'
    
    id = Column(Integer, primary_key=True)
    primary_faculty_id = Column(Integer, ForeignKey('faculty.id'))
    alternate_faculty_id = Column(Integer, ForeignKey('faculty.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    priority = Column(Integer, default=1)
    
    # Relationships with explicit foreign keys to avoid warnings
    primary_faculty = relationship("Faculty", foreign_keys=[primary_faculty_id], overlaps="primary_for")
    alternate_faculty = relationship("Faculty", foreign_keys=[alternate_faculty_id], overlaps="alternate_for")
    subject = relationship("Subject")

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True)
    name = Column(String(100))
    hod_id = Column(Integer, ForeignKey('faculty.id'), nullable=True)
    
    # Relationships
    batches = relationship("Batch", back_populates="department")
    hod = relationship("Faculty")

class Batch(Base):
    __tablename__ = 'batches'
    
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    year = Column(Integer)
    semester = Column(Integer)
    section = Column(String(5))
    strength = Column(Integer)
    
    # Relationships
    department = relationship("Department", back_populates="batches")

class Subject(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(100))
    credits = Column(Integer)
    total_hours = Column(Integer)
    difficulty_level = Column(Integer, default=3)
    
    # Relationships
    faculty = relationship("FacultySubject", back_populates="subject")
    sessions = relationship("SubjectSession", back_populates="subject")

class SubjectSession(Base):
    __tablename__ = 'subject_sessions'
    
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    session_type = Column(Enum(SessionType))
    duration_hours = Column(Float)
    weekly_frequency = Column(Integer)
    preferred_days = Column(JSON)
    preferred_times = Column(JSON)
    requires_lab = Column(Boolean, default=False)
    min_days_after_theory = Column(Integer, default=0)
    
    # Relationships
    subject = relationship("Subject", back_populates="sessions")

class Room(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(String(20), unique=True)
    room_type = Column(Enum(RoomType))
    capacity = Column(Integer)
    facilities = Column(JSON)
    is_available = Column(Boolean, default=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    
    # Relationships
    department = relationship("Department")

class Timetable(Base):
    __tablename__ = 'timetables'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    department_id = Column(Integer, ForeignKey('departments.id'))
    academic_year = Column(String(9))
    semester = Column(Integer)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.DRAFT)
    generated_data = Column(JSON)
    fitness_score = Column(Float)
    generated_by = Column(Integer, ForeignKey('users.id'))
    generated_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    # Relationships
    department = relationship("Department")
    generator_user = relationship("User", foreign_keys=[generated_by])
    approver_user = relationship("User", foreign_keys=[approved_by])

class TimetableEntry(Base):
    __tablename__ = 'timetable_entries'
    
    id = Column(Integer, primary_key=True)
    timetable_id = Column(Integer, ForeignKey('timetables.id'))
    day_of_week = Column(Integer)
    time_slot = Column(Integer)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    batch_id = Column(Integer, ForeignKey('batches.id'))
    session_type = Column(Enum(SessionType))
    is_fixed = Column(Boolean, default=False)
    
    # Relationships
    timetable = relationship("Timetable")
    subject = relationship("Subject")
    faculty = relationship("Faculty")
    room = relationship("Room")
    batch = relationship("Batch")

class TimetableApproval(Base):
    __tablename__ = 'timetable_approvals'
    
    id = Column(Integer, primary_key=True)
    timetable_id = Column(Integer, ForeignKey('timetables.id'))
    requested_by = Column(Integer, ForeignKey('users.id'))
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    status = Column(Enum(ApprovalStatus))
    comments = Column(String(500), nullable=True)
    
    # Relationships with explicit foreign keys
    timetable = relationship("Timetable")
    requester = relationship("User", foreign_keys=[requested_by], overlaps="approvals")
    approver = relationship("User", foreign_keys=[approved_by], overlaps="approvals")

class SystemConfiguration(Base):
    __tablename__ = 'system_configurations'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True)
    value = Column(JSON)
    description = Column(String(200))
    
    @classmethod
    def get_config(cls, session, key, default=None):
        config = session.query(cls).filter_by(key=key).first()
        return config.value if config else default

# Database initialization
def init_db(db_url="sqlite:///timetable_scheduler.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Password hashing utility
def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()