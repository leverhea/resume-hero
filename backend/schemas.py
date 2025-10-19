from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Union
from datetime import date
from enum import Enum

class ContactMethod(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    WEBSITE = "website"
    ADDRESS = "address"

class ContactInfo(BaseModel):
    type: ContactMethod
    value: str
    label: Optional[str] = None

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    location: Optional[str] = None
    description: Optional[str] = None

class WorkExperience(BaseModel):
    company: str
    position: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current: bool = False
    location: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = []
    technologies: List[str] = []

class Project(BaseModel):
    name: str
    description: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    technologies: List[str] = []
    url: Optional[str] = None
    github_url: Optional[str] = None

class Skill(BaseModel):
    name: str
    category: Optional[str] = None  # e.g., "Programming", "Languages", "Tools"
    proficiency: Optional[str] = None  # e.g., "Beginner", "Intermediate", "Advanced"

class Certification(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None

class Language(BaseModel):
    name: str
    proficiency: Optional[str] = None  # e.g., "Native", "Fluent", "Intermediate"

class ResumeData(BaseModel):
    # Personal Information
    full_name: Optional[str] = None
    contact_info: List[ContactInfo] = []
    
    # Professional Summary
    summary: Optional[str] = None
    objective: Optional[str] = None
    
    # Core Sections
    education: List[Education] = []
    work_experience: List[WorkExperience] = []
    projects: List[Project] = []
    skills: List[Skill] = []
    certifications: List[Certification] = []
    languages: List[Language] = []
    
    # Additional Sections
    awards: List[str] = []
    publications: List[str] = []
    volunteer_experience: List[WorkExperience] = []
    interests: List[str] = []
    
    # Metadata
    parsing_confidence: Optional[float] = None
    raw_text: Optional[str] = None
    file_name: Optional[str] = None
    parsed_date: Optional[date] = None
    
    class Config:
        # Allow extra fields and make all fields optional
        extra = "allow"
        validate_assignment = True

class ResumeUploadResponse(BaseModel):
    success: bool
    message: str
    resume_data: Optional[ResumeData] = None
    error: Optional[str] = None
