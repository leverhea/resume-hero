// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const parseButton = document.getElementById('parseButton');
const loading = document.getElementById('loading');
const resultSection = document.getElementById('resultSection');
const resumeData = document.getElementById('resumeData');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');

// API configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let selectedFile = null;

// Event listeners
fileInput.addEventListener('change', handleFileSelect);
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
parseButton.addEventListener('click', handleParse);

// File selection handlers
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function processFile(file) {
    // Validate file type
    if (!file.type.includes('pdf')) {
        showError('Please select a PDF file');
        return;
    }
    
    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showError('File size must be less than 10MB');
        return;
    }
    
    selectedFile = file;
    
    // Update UI
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    uploadArea.style.display = 'none';
    fileInfo.style.display = 'flex';
    
    hideError();
    hideResult();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Parse resume
async function handleParse() {
    if (!selectedFile) {
        showError('Please select a file first');
        return;
    }
    
    // Show loading state
    showLoading();
    hideError();
    hideResult();
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch(`${API_BASE_URL}/parse-resume`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayResumeData(data.resume_data);
        } else {
            showError(data.message || 'Failed to parse resume');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to parse resume. Please check if the server is running.');
    } finally {
        hideLoading();
    }
}

// Display resume data
function displayResumeData(data) {
    let html = '';
    
    // Personal Information
    if (data.full_name || data.contact_info.length > 0) {
        html += '<div class="data-section">';
        html += '<div class="section-title">Personal Information</div>';
        
        if (data.full_name) {
            html += `<div class="data-item">
                <span class="data-label">Name:</span>
                <span class="data-value">${data.full_name}</span>
            </div>`;
        }
        
        if (data.contact_info.length > 0) {
            html += '<div class="data-item">';
            html += '<span class="data-label">Contact:</span>';
            html += '<div class="contact-info">';
            data.contact_info.forEach(contact => {
                html += `<span class="contact-item">${contact.value}</span>`;
            });
            html += '</div></div>';
        }
        
        html += '</div>';
    }
    
    // Summary
    if (data.summary) {
        html += '<div class="data-section">';
        html += '<div class="section-title">Summary</div>';
        html += `<div class="data-item">${data.summary}</div>`;
        html += '</div>';
    }
    
    // Education
    if (data.education.length > 0) {
        html += '<div class="data-section">';
        html += '<div class="section-title">Education</div>';
        data.education.forEach(edu => {
            html += '<div class="data-item">';
            if (edu.institution) {
                html += `<div><span class="data-label">Institution:</span> ${edu.institution}</div>`;
            }
            if (edu.degree) {
                html += `<div><span class="data-label">Degree:</span> ${edu.degree}</div>`;
            }
            if (edu.field_of_study) {
                html += `<div><span class="data-label">Field:</span> ${edu.field_of_study}</div>`;
            }
            if (edu.start_date || edu.end_date) {
                const dates = [edu.start_date, edu.end_date].filter(Boolean).join(' - ');
                html += `<div><span class="data-label">Dates:</span> ${dates}</div>`;
            }
            html += '</div>';
        });
        html += '</div>';
    }
    
    // Work Experience
    if (data.work_experience.length > 0) {
        html += '<div class="data-section">';
        html += '<div class="section-title">Work Experience</div>';
        data.work_experience.forEach(work => {
            html += '<div class="data-item">';
            if (work.company) {
                html += `<div><span class="data-label">Company:</span> ${work.company}</div>`;
            }
            if (work.position) {
                html += `<div><span class="data-label">Position:</span> ${work.position}</div>`;
            }
            if (work.start_date || work.end_date) {
                const dates = [work.start_date, work.end_date].filter(Boolean).join(' - ');
                html += `<div><span class="data-label">Dates:</span> ${dates}</div>`;
            }
            if (work.description) {
                html += `<div><span class="data-label">Description:</span> ${work.description}</div>`;
            }
            html += '</div>';
        });
        html += '</div>';
    }
    
    // Skills
    if (data.skills.length > 0) {
        html += '<div class="data-section">';
        html += '<div class="section-title">Skills</div>';
        html += '<div class="data-item">';
        html += '<div class="skills-list">';
        data.skills.forEach(skill => {
            html += `<span class="skill-tag">${skill.name}</span>`;
        });
        html += '</div></div></div>';
    }
    
    // Projects
    if (data.projects.length > 0) {
        html += '<div class="data-section">';
        html += '<div class="section-title">Projects</div>';
        data.projects.forEach(project => {
            html += '<div class="data-item">';
            if (project.name) {
                html += `<div><span class="data-label">Project:</span> ${project.name}</div>`;
            }
            if (project.description) {
                html += `<div><span class="data-label">Description:</span> ${project.description}</div>`;
            }
            if (project.technologies.length > 0) {
                html += '<div><span class="data-label">Technologies:</span> ';
                html += project.technologies.join(', ');
                html += '</div>';
            }
            html += '</div>';
        });
        html += '</div>';
    }
    
    // Certifications
    if (data.certifications.length > 0) {
        html += '<div class="data-section">';
        html += '<div class="section-title">Certifications</div>';
        data.certifications.forEach(cert => {
            html += '<div class="data-item">';
            if (cert.name) {
                html += `<div><span class="data-label">Certification:</span> ${cert.name}</div>`;
            }
            if (cert.issuer) {
                html += `<div><span class="data-label">Issuer:</span> ${cert.issuer}</div>`;
            }
            html += '</div>';
        });
        html += '</div>';
    }
    
    // Languages
    if (data.languages.length > 0) {
        html += '<div class="data-section">';
        html += '<div class="section-title">Languages</div>';
        html += '<div class="data-item">';
        data.languages.forEach(lang => {
            html += `<span class="skill-tag">${lang.name}</span>`;
        });
        html += '</div></div>';
    }
    
    resumeData.innerHTML = html;
    resultSection.style.display = 'block';
}

// UI state management
function showLoading() {
    loading.style.display = 'block';
    parseButton.disabled = true;
}

function hideLoading() {
    loading.style.display = 'none';
    parseButton.disabled = false;
}

function showError(message) {
    errorMessage.textContent = message;
    error.style.display = 'block';
}

function hideError() {
    error.style.display = 'none';
}

function hideResult() {
    resultSection.style.display = 'none';
}

// Reset function
function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
    hideError();
    hideResult();
}
