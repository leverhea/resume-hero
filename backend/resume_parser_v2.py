import re
import pdfplumber
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from schemas import ResumeData, ContactInfo, Education, WorkExperience, Project, Skill, Certification, Language, ContactMethod
import logging

logger = logging.getLogger(__name__)

class SmartResumeParser:
    def __init__(self):
        # Contact patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        
        # Date patterns
        self.date_patterns = [
            re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b', re.IGNORECASE),
            re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
            re.compile(r'\b\d{4}\b')
        ]
        
        # Section headers
        self.section_headers = {
            'education': ['education', 'academic', 'university', 'college', 'degree', 'bachelor', 'master', 'phd', 'diploma', 'certificate'],
            'experience': ['experience', 'employment', 'work history', 'career', 'professional', 'employment history'],
            'skills': ['skills', 'technical skills', 'technologies', 'programming', 'tools', 'technical expertise'],
            'projects': ['projects', 'portfolio', 'personal projects', 'key projects'],
            'certifications': ['certifications', 'certificates', 'credentials', 'licenses', 'certifications & licenses'],
            'languages': ['languages', 'language skills', 'foreign languages'],
            'summary': ['summary', 'profile', 'about', 'professional summary', 'executive summary'],
            'objective': ['objective', 'career objective', 'goal']
        }
        
        # Common tech skills
        self.tech_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#', 'PHP', 'Ruby',
            'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'Laravel',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Ansible',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra',
            'Apache', 'Nginx', 'Kafka', 'RabbitMQ', 'Apache Spark', 'Hadoop',
            'Git', 'GitHub', 'GitLab', 'Jenkins', 'CI/CD', 'DevOps',
            'Machine Learning', 'AI', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
            'SQL', 'NoSQL', 'BigQuery', 'Snowflake', 'Redshift', 'Airflow', 'dbt'
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
            
            # Clean and normalize text
            cleaned_text = self._clean_text(raw_text)
            
            # Extract basic information
            full_name = self._extract_name(cleaned_text)
            contact_info = self._extract_contact_info(cleaned_text)
            
            # Extract sections
            sections = self._identify_sections(cleaned_text)
            
            # Parse each section
            education = self._parse_education(sections.get('education', ''))
            work_experience = self._parse_work_experience(sections.get('experience', ''))
            skills = self._parse_skills(sections.get('skills', ''), cleaned_text)
            projects = self._parse_projects(sections.get('projects', ''))
            certifications = self._parse_certifications(sections.get('certifications', ''))
            languages = self._parse_languages(sections.get('languages', ''))
            summary = self._extract_summary(sections.get('summary', ''))
            
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
                parsing_confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s@.-]', ' ', text)
        return text.strip()
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract full name from text."""
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            # Look for name patterns (2-4 words, title case, no special chars)
            if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){1,3}$', line) and len(line) < 50:
                return line
        return None
    
    def _extract_contact_info(self, text: str) -> List[ContactInfo]:
        """Extract contact information."""
        contact_info = []
        
        # Extract emails
        emails = set(self.email_pattern.findall(text))
        for email in emails:
            contact_info.append(ContactInfo(
                type=ContactMethod.EMAIL,
                value=email,
                label="Email"
            ))
        
        # Extract phone numbers
        phones = self.phone_pattern.findall(text)
        for phone in phones:
            phone_str = ''.join(phone).strip()
            if phone_str and len(phone_str) >= 10:
                contact_info.append(ContactInfo(
                    type=ContactMethod.PHONE,
                    value=phone_str,
                    label="Phone"
                ))
        
        # Extract LinkedIn
        linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)
        linkedin_matches = linkedin_pattern.findall(text)
        for linkedin in set(linkedin_matches):
            contact_info.append(ContactInfo(
                type=ContactMethod.LINKEDIN,
                value=f"https://{linkedin}",
                label="LinkedIn"
            ))
        
        return contact_info
    
    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identify different sections of the resume."""
        sections = {}
        lines = text.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            section_type = self._is_section_header(line)
            
            if section_type:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = section_type
                current_content = []
            else:
                # Add to current section
                if current_section:
                    current_content.append(line)
                else:
                    # If no section identified yet, this might be the header/contact area
                    if not sections.get('header'):
                        sections['header'] = line
                    else:
                        sections['header'] += '\n' + line
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _is_section_header(self, line: str) -> Optional[str]:
        """Check if line is a section header."""
        line_lower = line.lower()
        
        for section, keywords in self.section_headers.items():
            if any(keyword in line_lower for keyword in keywords):
                return section
        
        return None
    
    def _parse_education(self, education_text: str) -> List[Education]:
        """Parse education section."""
        if not education_text:
            return []
        
        education = []
        lines = education_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for degree patterns
            degree_match = re.search(r'\b(bachelor|master|phd|doctorate|associate|diploma|certificate|degree)\b', line, re.IGNORECASE)
            if degree_match:
                # Try to extract institution and degree
                parts = line.split()
                degree = degree_match.group(1).title()
                
                # Find institution (usually before degree)
                degree_index = parts.index(degree_match.group(1))
                institution = ' '.join(parts[:degree_index]) if degree_index > 0 else line
                
                education.append(Education(
                    institution=institution,
                    degree=degree
                ))
        
        return education
    
    def _parse_work_experience(self, experience_text: str) -> List[WorkExperience]:
        """Parse work experience section."""
        if not experience_text:
            return []
        
        experience = []
        lines = experience_text.split('\n')
        
        current_job = None
        current_description = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for job title patterns (contains common job keywords)
            job_keywords = ['manager', 'engineer', 'developer', 'analyst', 'consultant', 'director', 'lead', 'senior', 'staff']
            if any(keyword in line.lower() for keyword in job_keywords) and '•' in line:
                # Save previous job
                if current_job:
                    current_job.description = ' '.join(current_description)
                    experience.append(current_job)
                
                # Start new job
                parts = line.split('•')
                if len(parts) >= 2:
                    company = parts[0].strip()
                    position = parts[1].strip()
                    
                    current_job = WorkExperience(
                        company=company,
                        position=position
                    )
                    current_description = []
            else:
                # Add to current job description
                if current_job:
                    current_description.append(line)
        
        # Save last job
        if current_job:
            current_job.description = ' '.join(current_description)
            experience.append(current_job)
        
        return experience
    
    def _parse_skills(self, skills_text: str, full_text: str) -> List[Skill]:
        """Parse skills section."""
        skills = []
        
        # If we have a dedicated skills section, use it
        if skills_text:
            skill_lines = skills_text.split('\n')
            for line in skill_lines:
                line = line.strip()
                if line:
                    # Split by common delimiters
                    skill_names = re.split(r'[,;|]', line)
                    for skill_name in skill_names:
                        skill_name = skill_name.strip()
                        if skill_name and len(skill_name) > 1:
                            skills.append(Skill(name=skill_name))
        
        # Also extract tech skills from the entire text
        for tech_skill in self.tech_skills:
            if tech_skill.lower() in full_text.lower():
                # Check if we already have this skill
                if not any(skill.name.lower() == tech_skill.lower() for skill in skills):
                    skills.append(Skill(name=tech_skill))
        
        return skills
    
    def _parse_projects(self, projects_text: str) -> List[Project]:
        """Parse projects section."""
        if not projects_text:
            return []
        
        projects = []
        lines = projects_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Skip very short lines
                projects.append(Project(
                    name=line,
                    description=line
                ))
        
        return projects
    
    def _parse_certifications(self, certs_text: str) -> List[Certification]:
        """Parse certifications section."""
        if not certs_text:
            return []
        
        certifications = []
        lines = certs_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                certifications.append(Certification(
                    name=line,
                    issuer="Unknown"
                ))
        
        return certifications
    
    def _parse_languages(self, languages_text: str) -> List[Language]:
        """Parse languages section."""
        if not languages_text:
            return []
        
        languages = []
        lines = languages_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line:
                # Split by common delimiters
                lang_names = re.split(r'[,;|]', line)
                for lang_name in lang_names:
                    lang_name = lang_name.strip()
                    if lang_name and len(lang_name) > 1:
                        languages.append(Language(name=lang_name))
        
        return languages
    
    def _extract_summary(self, summary_text: str) -> Optional[str]:
        """Extract professional summary."""
        if not summary_text:
            return None
        
        # Clean up the summary text
        summary = summary_text.strip()
        if len(summary) > 20:  # Only return if substantial content
            return summary
        
        return None
