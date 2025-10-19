#!/usr/bin/env python3
"""
Simple resume parser that extracts text from PDF and sends to LLM for parsing.
"""

import nltk
from pyresparser import utils
import requests
import json

# Download NLTK data once
nltk.download('stopwords', quiet=True)

class ResumeParser:
    """Simple resume parser that uses LLM for parsing."""
    
    def __init__(self, resume_path, llm_api_key=None, llm_endpoint=None):
        self.resume_path = resume_path
        self.llm_api_key = llm_api_key
        self.llm_endpoint = llm_endpoint
    
    def get_extracted_data(self):
        """Extract text from PDF and parse with LLM."""
        # Extract text using PyResParser
        text = utils.extract_text_from_pdf(self.resume_path)
        if hasattr(text, '__iter__') and not isinstance(text, str):
            text = ' '.join(text)
        
        # If no LLM configured, return basic info
        if not self.llm_api_key or not self.llm_endpoint:
            return self._extract_basic_info(text)
        
        # Send to LLM for parsing
        return self._parse_with_llm(text)
    
    def _extract_basic_info(self, text):
        """Extract basic info using simple regex as fallback."""
        import re
        
        # Extract email
        email = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Extract phone
        phone = re.findall(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', text)
        
        # Extract name (first line that looks like a name)
        lines = text.split('\n')
        name = None
        for line in lines[:5]:
            line = line.strip()
            if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){1,3}$', line) and len(line) < 50:
                name = line
                break
        
        return {
            'name': name,
            'email': email[0] if email else None,
            'mobile_number': ''.join(phone[0]) if phone else None,
            'raw_text': text,
            'parsing_method': 'basic_regex'
        }
    
    def _parse_with_llm(self, text):
        """Parse resume text using LLM."""
        prompt = f"""
        Please parse the following resume text and extract structured information. 
        Return a JSON object with the following fields:
        - name: Full name
        - email: Email address
        - mobile_number: Phone number
        - skills: List of technical skills
        - experience: List of work experience entries
        - education: List of education entries
        - summary: Professional summary or objective
        
        Resume text:
        {text}
        
        Return only valid JSON, no other text.
        """
        
        try:
            # This is a placeholder - you'd implement your LLM API call here
            # For now, return basic info
            return self._extract_basic_info(text)
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return self._extract_basic_info(text)

# Example usage
if __name__ == "__main__":
    # Parse resume - exactly as you wanted!
    data = ResumeParser('/var/home/leverhea/Downloads/Lucas_Everheart.pdf').get_extracted_data()
    
    # Print results
    print("📄 PARSED RESUME DATA")
    print("=" * 50)
    for key, value in data.items():
        if key != 'raw_text':
            print(f"{key}: {value}")
        else:
            print(f"{key}: {value[:200]}...")
