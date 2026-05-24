from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    qualification = Column(String(200), nullable=False)
    experience    = Column(String(100), nullable=False)
    skills        = Column(Text,        nullable=False)
    role          = Column(String(100), nullable=False)

    sessions = relationship("InterviewSession", back_populates="candidate")


class InterviewSession(Base):
    __tablename__ = "sessions"

    session_id       = Column(String(36), primary_key=True)
    candidate_id     = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    status           = Column(String(20), default="in_progress")   # in_progress | completed
    current_question = Column(Integer,   default=0)
    total_questions  = Column(Integer,   nullable=False)
    started_at       = Column(DateTime,  default=datetime.utcnow)
    completed_at     = Column(DateTime,  nullable=True)

    candidate = relationship("Candidate", back_populates="sessions")
    answers   = relationship("QuestionAnswer", back_populates="session")
    report    = relationship("Report", back_populates="session", uselist=False)



class QuestionAnswer(Base):
    __tablename__ = "questions_answers"

    id             = Column(Integer,    primary_key=True, index=True)
    session_id     = Column(String(36), ForeignKey("sessions.session_id"), nullable=False)
    question_index = Column(Integer,    nullable=False)
    question_text  = Column(Text,       nullable=False)
    answer_text    = Column(Text,       nullable=True)
    score          = Column(Float,      nullable=True)
    feedback       = Column(Text,       nullable=True)

    session = relationship("InterviewSession", back_populates="answers")


class Report(Base):
    __tablename__ = "reports"

    id                  = Column(Integer,    primary_key=True, index=True)
    session_id          = Column(String(36), ForeignKey("sessions.session_id"), nullable=False)
    overall_score       = Column(Float,      nullable=False)
    hire_recommendation = Column(String(20), nullable=False)   # hire | maybe | reject
    strengths           = Column(Text,       nullable=False)
    weaknesses          = Column(Text,       nullable=False)

    session = relationship("InterviewSession", back_populates="report")