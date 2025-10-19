import re
import pdfplumber
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from schemas import ResumeData, ContactInfo, Education, WorkExperience, Project, Skill, Certification, Language, ContactMethod
import logging

logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.date_patterns = [
            re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b', re.IGNORECASE),
            re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
            re.compile(r'\b\d{4}\b')
        ]
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def parse_resume(self, pdf_path: str, file_name: str) -> ResumeData:
        """Parse resume from PDF and return structured data."""
        try:
            raw_text = self.extract_text_from_pdf(pdf_path)
            
            # Extract basic information
            contact_info = self._extract_contact_info(raw_text)
            full_name = self._extract_name(raw_text)
            summary = self._extract_summary(raw_text)
            
            # Extract structured sections
            education = self._extract_education(raw_text)
            work_experience = self._extract_work_experience(raw_text)
            skills = self._extract_skills(raw_text)
            projects = self._extract_projects(raw_text)
            certifications = self._extract_certifications(raw_text)
            languages = self._extract_languages(raw_text)
            
            return ResumeData(
                full_name=full_name,
                contact_info=contact_info,
                summary=summary,
                education=education,
                work_experience=work_experience,
                skills=skills,
                projects=projects,
                certifications=certifications,
                languages=languages,
                raw_text=raw_text,
                file_name=file_name,
                parsed_date=date.today(),
                parsing_confidence=0.7  # Basic confidence score
            )
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise
    
    def _extract_contact_info(self, text: str) -> List[ContactInfo]:
        """Extract contact information from text."""
        contact_info = []
        
        # Extract email
        emails = self.email_pattern.findall(text)
        for email in emails:
            contact_info.append(ContactInfo(
                type=ContactMethod.EMAIL,
                value=email,
                label="Email"
            ))
        
        # Extract phone numbers
        phones = self.phone_pattern.findall(text)
        for phone in phones:
            phone_str = ''.join(phone)
            if phone_str:
                contact_info.append(ContactInfo(
                    type=ContactMethod.PHONE,
                    value=phone_str,
                    label="Phone"
                ))
        
        # Extract LinkedIn
        linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)
        linkedin_matches = linkedin_pattern.findall(text)
        for linkedin in linkedin_matches:
            contact_info.append(ContactInfo(
                type=ContactMethod.LINKEDIN,
                value=f"https://{linkedin}",
                label="LinkedIn"
            ))
        
        # Extract GitHub
        github_pattern = re.compile(r'github\.com/[\w-]+', re.IGNORECASE)
        github_matches = github_pattern.findall(text)
        for github in github_matches:
            contact_info.append(ContactInfo(
                type=ContactMethod.GITHUB,
                value=f"https://{github}",
                label="GitHub"
            ))
        
        return contact_info
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract full name from text (usually first line or near top)."""
        lines = text.split('\n')[:10]  # Check first 10 lines
        for line in lines:
            line = line.strip()
            if len(line) > 2 and len(line.split()) >= 2:
                # Check if line looks like a name (no special characters, reasonable length)
                if re.match(r'^[A-Za-z\s\.]+$', line) and len(line) < 50:
                    return line
        return None
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary or objective."""
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in summary_keywords):
                # Look for content in next few lines
                summary_lines = []
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not self._is_section_header(next_line):
                        summary_lines.append(next_line)
                    else:
                        break
                if summary_lines:
                    return ' '.join(summary_lines)
        return None
    
    def _extract_education(self, text: str) -> List[Education]:
        """Extract education information."""
        education = []
        education_keywords = ['education', 'academic', 'university', 'college', 'degree', 'bachelor', 'master', 'phd', 'diploma']
        
        lines = text.split('\n')
        in_education_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering education section
            if any(keyword in line_lower for keyword in education_keywords):
                in_education_section = True
                continue
            
            # Check if we're leaving education section
            if in_education_section and self._is_section_header(line) and not any(keyword in line_lower for keyword in education_keywords):
                break
            
            if in_education_section and line.strip():
                # Try to parse education entry
                edu_entry = self._parse_education_line(line)
                if edu_entry:
                    education.append(edu_entry)
        
        return education
    
    def _extract_work_experience(self, text: str) -> List[WorkExperience]:
        """Extract work experience information."""
        experience = []
        work_keywords = ['experience', 'employment', 'work history', 'career', 'professional']
        
        lines = text.split('\n')
        in_experience_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering experience section
            if any(keyword in line_lower for keyword in work_keywords):
                in_experience_section = True
                continue
            
            # Check if we're leaving experience section
            if in_experience_section and self._is_section_header(line) and not any(keyword in line_lower for keyword in work_keywords):
                break
            
            if in_experience_section and line.strip():
                # Try to parse work experience entry
                work_entry = self._parse_work_experience_line(line)
                if work_entry:
                    experience.append(work_entry)
        
        return experience
    
    def _extract_skills(self, text: str) -> List[Skill]:
        """Extract skills information."""
        skills = []
        skill_keywords = ['skills', 'technical skills', 'technologies', 'programming', 'tools']
        
        lines = text.split('\n')
        in_skills_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering skills section
            if any(keyword in line_lower for keyword in skill_keywords):
                in_skills_section = True
                continue
            
            # Check if we're leaving skills section
            if in_skills_section and self._is_section_header(line) and not any(keyword in line_lower for keyword in skill_keywords):
                break
            
            if in_skills_section and line.strip():
                # Parse skills from line (comma or pipe separated)
                skill_names = re.split(r'[,|;]', line)
                for skill_name in skill_names:
                    skill_name = skill_name.strip()
                    if skill_name and len(skill_name) > 1:
                        skills.append(Skill(name=skill_name))
        
        return skills
    
    def _extract_projects(self, text: str) -> List[Project]:
        """Extract projects information."""
        projects = []
        project_keywords = ['projects', 'portfolio', 'personal projects']
        
        lines = text.split('\n')
        in_projects_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering projects section
            if any(keyword in line_lower for keyword in project_keywords):
                in_projects_section = True
                continue
            
            # Check if we're leaving projects section
            if in_projects_section and self._is_section_header(line) and not any(keyword in line_lower for keyword in project_keywords):
                break
            
            if in_projects_section and line.strip():
                # Try to parse project entry
                project_entry = self._parse_project_line(line)
                if project_entry:
                    projects.append(project_entry)
        
        return projects
    
    def _extract_certifications(self, text: str) -> List[Certification]:
        """Extract certifications information."""
        certifications = []
        cert_keywords = ['certifications', 'certificates', 'credentials', 'licenses']
        
        lines = text.split('\n')
        in_cert_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering certifications section
            if any(keyword in line_lower for keyword in cert_keywords):
                in_cert_section = True
                continue
            
            # Check if we're leaving certifications section
            if in_cert_section and self._is_section_header(line) and not any(keyword in line_lower for keyword in cert_keywords):
                break
            
            if in_cert_section and line.strip():
                # Try to parse certification entry
                cert_entry = self._parse_certification_line(line)
                if cert_entry:
                    certifications.append(cert_entry)
        
        return certifications
    
    def _extract_languages(self, text: str) -> List[Language]:
        """Extract languages information."""
        languages = []
        lang_keywords = ['languages', 'language skills']
        
        lines = text.split('\n')
        in_lang_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering languages section
            if any(keyword in line_lower for keyword in lang_keywords):
                in_lang_section = True
                continue
            
            # Check if we're leaving languages section
            if in_lang_section and self._is_section_header(line) and not any(keyword in line_lower for keyword in lang_keywords):
                break
            
            if in_lang_section and line.strip():
                # Parse languages from line
                lang_names = re.split(r'[,|;]', line)
                for lang_name in lang_names:
                    lang_name = lang_name.strip()
                    if lang_name and len(lang_name) > 1:
                        languages.append(Language(name=lang_name))
        
        return languages
    
    def _is_section_header(self, line: str) -> bool:
        """Check if line is likely a section header."""
        line = line.strip()
        if not line:
            return False
        
        # Check for common section header patterns
        header_patterns = [
            r'^[A-Z\s]+$',  # All caps
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$',  # Title Case
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s*:$',  # Title Case with colon
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, line) and len(line) < 50:
                return True
        
        return False
    
    def _parse_education_line(self, line: str) -> Optional[Education]:
        """Parse a single education line."""
        # This is a simplified parser - in practice, you'd want more sophisticated parsing
        line = line.strip()
        if len(line) < 10:  # Too short to be meaningful
            return None
        
        # Look for degree keywords
        degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma', 'certificate']
        degree = None
        for keyword in degree_keywords:
            if keyword.lower() in line.lower():
                degree = keyword.title()
                break
        
        if not degree:
            degree = "Degree"  # Default if no degree found
        
        return Education(
            institution=line,  # Simplified - would need more parsing
            degree=degree
        )
    
    def _parse_work_experience_line(self, line: str) -> Optional[WorkExperience]:
        """Parse a single work experience line."""
        line = line.strip()
        if len(line) < 10:  # Too short to be meaningful
            return None
        
        # This is a simplified parser
        return WorkExperience(
            company=line,  # Simplified - would need more parsing
            position="Position"  # Would need to extract from line
        )
    
    def _parse_project_line(self, line: str) -> Optional[Project]:
        """Parse a single project line."""
        line = line.strip()
        if len(line) < 5:  # Too short to be meaningful
            return None
        
        return Project(
            name=line,  # Simplified - would need more parsing
            description=line
        )
    
    def _parse_certification_line(self, line: str) -> Optional[Certification]:
        """Parse a single certification line."""
        line = line.strip()
        if len(line) < 5:  # Too short to be meaningful
            return None
        
        return Certification(
            name=line,  # Simplified - would need more parsing
            issuer="Unknown"  # Would need to extract from line
        )
