// Global variables
let subjectCount = 1;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    attachEventListeners();
    updateMarksCalculation();
    initializeExcelUpload();
    initializeMobileMenu();
});

// Initialize form functionality
function initializeForm() {
    // Add validation to all existing mark inputs
    const markInputs = document.querySelectorAll('.marks-input, .max-marks-input');
    markInputs.forEach(input => {
        attachMarkValidation(input);
    });
    
    // Set default values
    const maxMarkInputs = document.querySelectorAll('.max-marks-input');
    maxMarkInputs.forEach(input => {
        if (!input.value) {
            input.value = 100;
        }
    });
}

// Attach event listeners
function attachEventListeners() {
    // Add Subject button
    const addSubjectBtn = document.getElementById('addSubject');
    if (addSubjectBtn) {
        addSubjectBtn.addEventListener('click', addSubject);
    }
    
    // Reset Form button
    const resetBtn = document.getElementById('resetForm');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetForm);
    }
    
    // Form submission
    const marksheetForm = document.getElementById('marksheetForm');
    if (marksheetForm) {
        marksheetForm.addEventListener('submit', validateForm);
    }
    
    // File input validation
    const templateInput = document.getElementById('template');
    if (templateInput) {
        templateInput.addEventListener('change', validateFile);
    }
    
    // Real-time marks calculation
    document.addEventListener('input', function(e) {
        if (e.target.matches('.marks-input') || e.target.matches('.max-marks-input')) {
            updateMarksCalculation();
        }
    });
}

// Add new subject row
function addSubject() {
    subjectCount++;
    
    const subjectsContainer = document.getElementById('subjectsContainer');
    const subjectRow = document.createElement('div');
    subjectRow.className = 'subject-row fade-in';
    
    subjectRow.innerHTML = `
        <div class="form-group">
            <label>Subject Name *</label>
            <input type="text" name="subject_name[]" required placeholder="e.g., Physics">
        </div>
        <div class="form-group">
            <label>Marks Obtained *</label>
            <input type="number" name="marks[]" min="0" max="100" required class="marks-input">
        </div>
        <div class="form-group">
            <label>Maximum Marks *</label>
            <input type="number" name="max_marks[]" min="1" value="100" required class="max-marks-input">
        </div>
        <div class="form-group">
            <button type="button" class="remove-subject" onclick="removeSubject(this)">Remove</button>
        </div>
    `;
    
    subjectsContainer.appendChild(subjectRow);
    
    // Attach validation to new inputs
    const newMarkInputs = subjectRow.querySelectorAll('.marks-input, .max-marks-input');
    newMarkInputs.forEach(input => {
        attachMarkValidation(input);
    });
    
    // Focus on the new subject name input
    subjectRow.querySelector('input[name="subject_name[]"]').focus();
    
    updateMarksCalculation();
    
    // Show success message
    showNotification('Subject added successfully!', 'success');
}

// Remove subject row
function removeSubject(button) {
    const subjectRows = document.querySelectorAll('.subject-row');
    
    if (subjectRows.length <= 1) {
        showNotification('At least one subject is required!', 'error');
        return;
    }
    
    const subjectRow = button.closest('.subject-row');
    subjectRow.style.animation = 'slideOut 0.3s ease-out';
    
    setTimeout(() => {
        subjectRow.remove();
        updateMarksCalculation();
        showNotification('Subject removed!', 'info');
    }, 300);
}

// Attach mark validation to input
function attachMarkValidation(input) {
    input.addEventListener('input', function() {
        validateMarkInput(this);
    });
    
    input.addEventListener('blur', function() {
        validateMarkInput(this);
        updateMarksCalculation();
    });
}

// Validate individual mark input
function validateMarkInput(input) {
    const value = parseInt(input.value);
    const min = parseInt(input.min) || 0;
    const max = parseInt(input.max) || 100;
    
    // Remove previous error states
    input.classList.remove('error');
    
    // Check if value is valid
    if (isNaN(value) || value < min || value > max) {
        input.classList.add('error');
        return false;
    }
    
    // Special validation for marks vs max marks
    if (input.classList.contains('marks-input')) {
        const row = input.closest('.subject-row');
        const maxMarksInput = row.querySelector('.max-marks-input');
        const maxMarks = parseInt(maxMarksInput.value) || 100;
        
        if (value > maxMarks) {
            input.classList.add('error');
            showNotification(`Marks cannot exceed ${maxMarks}!`, 'error');
            return false;
        }
    }
    
    return true;
}

// Update marks calculation
function updateMarksCalculation() {
    const markInputs = document.querySelectorAll('.marks-input');
    const maxMarkInputs = document.querySelectorAll('.max-marks-input');
    
    let totalMarks = 0;
    let totalMaxMarks = 0;
    let validInputs = true;
    
    markInputs.forEach((input, index) => {
        const marks = parseInt(input.value) || 0;
        const maxMarks = parseInt(maxMarkInputs[index]?.value) || 100;
        
        if (!isNaN(marks) && !isNaN(maxMarks) && marks >= 0 && marks <= maxMarks) {
            totalMarks += marks;
            totalMaxMarks += maxMarks;
        } else {
            validInputs = false;
        }
    });
    
    // Update display
    document.getElementById('totalMarks').textContent = totalMarks;
    document.getElementById('totalMaxMarks').textContent = totalMaxMarks;
    
    // Calculate percentage
    const percentage = totalMaxMarks > 0 ? (totalMarks / totalMaxMarks) * 100 : 0;
    document.getElementById('percentage').textContent = percentage.toFixed(2) + '%';
    
    // Calculate grade
    const gradeInfo = calculateGrade(percentage);
    const gradeElement = document.getElementById('grade');
    gradeElement.textContent = gradeInfo.grade;
    gradeElement.className = `grade-${gradeInfo.grade.toLowerCase().replace('+', 'plus')}`;
    
    // Add visual feedback for percentage
    const percentageElement = document.getElementById('percentage');
    percentageElement.className = getPercentageClass(percentage);
}

// Calculate grade based on percentage
function calculateGrade(percentage) {
    if (percentage >= 90) {
        return { grade: 'A+', remarks: 'Outstanding Performance' };
    } else if (percentage >= 80) {
        return { grade: 'A', remarks: 'Excellent Performance' };
    } else if (percentage >= 70) {
        return { grade: 'B+', remarks: 'Very Good Performance' };
    } else if (percentage >= 60) {
        return { grade: 'B', remarks: 'Good Performance' };
    } else if (percentage >= 50) {
        return { grade: 'C', remarks: 'Satisfactory Performance' };
    } else if (percentage >= 40) {
        return { grade: 'D', remarks: 'Needs Improvement' };
    } else {
        return { grade: 'F', remarks: 'Failed - Requires Re-examination' };
    }
}

// Get CSS class for percentage styling
function getPercentageClass(percentage) {
    if (percentage >= 90) return 'grade-aplus';
    if (percentage >= 80) return 'grade-a';
    if (percentage >= 70) return 'grade-bplus';
    if (percentage >= 60) return 'grade-b';
    if (percentage >= 50) return 'grade-c';
    if (percentage >= 40) return 'grade-d';
    return 'grade-f';
}

// Validate file upload
function validateFile(event) {
    const file = event.target.files[0];
    
    if (!file) return;
    
    // Check file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Only PNG and JPG files are allowed!', 'error');
        event.target.value = '';
        return;
    }
    
    // Check file size (16MB max)
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showNotification('File size must be less than 16MB!', 'error');
        event.target.value = '';
        return;
    }
    
    showNotification('Template uploaded successfully!', 'success');
}

// Validate entire form before submission
function validateForm(event) {
    const form = event.target;
    let isValid = true;
    const errors = [];
    
    // Validate student information
    const requiredFields = ['student_name', 'roll_no', 'branch', 'semester', 'exam_type'];
    requiredFields.forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (!field.value.trim()) {
            isValid = false;
            errors.push(`${fieldName.replace('_', ' ')} is required`);
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    });
    
    // Validate subjects
    const subjectNames = form.querySelectorAll('input[name="subject_name[]"]');
    const markInputs = form.querySelectorAll('input[name="marks[]"]');
    const maxMarkInputs = form.querySelectorAll('input[name="max_marks[]"]');
    
    let hasValidSubject = false;
    
    for (let i = 0; i < subjectNames.length; i++) {
        const subjectName = subjectNames[i].value.trim();
        const marks = parseInt(markInputs[i].value);
        const maxMarks = parseInt(maxMarkInputs[i].value);
        
        if (subjectName) {
            hasValidSubject = true;
            
            // Validate marks
            if (isNaN(marks) || marks < 0) {
                isValid = false;
                errors.push(`Invalid marks for ${subjectName}`);
                markInputs[i].classList.add('error');
            } else if (isNaN(maxMarks) || maxMarks < 1) {
                isValid = false;
                errors.push(`Invalid maximum marks for ${subjectName}`);
                maxMarkInputs[i].classList.add('error');
            } else if (marks > maxMarks) {
                isValid = false;
                errors.push(`Marks cannot exceed maximum marks for ${subjectName}`);
                markInputs[i].classList.add('error');
            } else {
                markInputs[i].classList.remove('error');
                maxMarkInputs[i].classList.remove('error');
            }
        }
    }
    
    if (!hasValidSubject) {
        isValid = false;
        errors.push('At least one subject is required');
    }
    
    // Show errors if validation fails
    if (!isValid) {
        event.preventDefault();
        showNotification(errors.join(', '), 'error');
        
        // Scroll to first error
        const firstError = form.querySelector('.error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
        
        return false;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Generating...';
    
    // Re-enable button after 10 seconds as fallback
    setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }, 10000);
    
    return true;
}

// Reset form
function resetForm() {
    if (confirm('Are you sure you want to reset all form data?')) {
        const form = document.getElementById('marksheetForm');
        form.reset();
        
        // Remove all subject rows except the first one
        const subjectRows = document.querySelectorAll('.subject-row');
        for (let i = 1; i < subjectRows.length; i++) {
            subjectRows[i].remove();
        }
        
        // Reset counters and calculations
        subjectCount = 1;
        updateMarksCalculation();
        
        // Remove error classes
        const errorInputs = form.querySelectorAll('.error');
        errorInputs.forEach(input => input.classList.remove('error'));
        
        // Reset max marks to default
        const maxMarkInputs = form.querySelectorAll('.max-marks-input');
        maxMarkInputs.forEach(input => {
            input.value = 100;
        });
        
        showNotification('Form reset successfully!', 'info');
        
        // Focus on first input
        form.querySelector('input').focus();
    }
}

// Show notification messages
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 1rem;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
        font-weight: 500;
    `;
    
    // Set colors based on type
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#dcfce7';
            notification.style.color = '#166534';
            notification.style.border = '1px solid #bbf7d0';
            break;
        case 'error':
            notification.style.backgroundColor = '#fee2e2';
            notification.style.color = '#991b1b';
            notification.style.border = '1px solid #fecaca';
            break;
        case 'warning':
            notification.style.backgroundColor = '#fef3c7';
            notification.style.color = '#92400e';
            notification.style.border = '1px solid #fde68a';
            break;
        default:
            notification.style.backgroundColor = '#dbeafe';
            notification.style.color = '#1e40af';
            notification.style.border = '1px solid #bfdbfe';
    }
    
    // Style the close button
    const closeBtn = notification.querySelector('button');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: inherit;
        opacity: 0.7;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    closeBtn.addEventListener('mouseover', () => {
        closeBtn.style.opacity = '1';
    });
    
    closeBtn.addEventListener('mouseout', () => {
        closeBtn.style.opacity = '0.7';
    });
    
    // Add to document
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 5000);
}

// Excel Upload Functionality
function initializeExcelUpload() {
    const toggleBtn = document.getElementById('toggleExcelUpload');
    const uploadSection = document.getElementById('excelUploadSection');
    const excelFileInput = document.getElementById('excelFile');
    const importBtn = document.getElementById('importExcel');
    const downloadTemplateBtn = document.getElementById('downloadTemplate');
    const uploadDropzone = document.querySelector('.upload-dropzone');

    // Toggle Excel upload section
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            if (uploadSection.style.display === 'none') {
                uploadSection.style.display = 'block';
                toggleBtn.textContent = '❌ Close Excel Import';
                toggleBtn.classList.remove('btn-primary');
                toggleBtn.classList.add('btn-secondary');
            } else {
                uploadSection.style.display = 'none';
                toggleBtn.textContent = '📊 Import from Excel';
                toggleBtn.classList.remove('btn-secondary');
                toggleBtn.classList.add('btn-primary');
            }
        });
    }

    // File selection
    if (excelFileInput) {
        excelFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFileSelection(file);
            }
        });
    }

    // Drag and drop functionality
    if (uploadDropzone) {
        uploadDropzone.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadDropzone.classList.add('dragover');
        });

        uploadDropzone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadDropzone.classList.remove('dragover');
        });

        uploadDropzone.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadDropzone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (isValidExcelFile(file)) {
                    excelFileInput.files = files;
                    handleFileSelection(file);
                } else {
                    showUploadError('Please select a valid Excel file (.xlsx or .xls)');
                }
            }
        });
    }

    // Import button
    if (importBtn) {
        importBtn.addEventListener('click', function() {
            const file = excelFileInput.files[0];
            if (file) {
                importExcelData(file);
            }
        });
    }

    // Download template button
    if (downloadTemplateBtn) {
        downloadTemplateBtn.addEventListener('click', downloadExcelTemplate);
    }
}

function handleFileSelection(file) {
    const importBtn = document.getElementById('importExcel');
    const uploadDropzone = document.querySelector('.upload-dropzone');
    
    if (isValidExcelFile(file)) {
        // Update UI to show file selected
        uploadDropzone.innerHTML = `
            <div class="upload-icon">✅</div>
            <p class="upload-text">File Selected: ${file.name}</p>
            <p class="upload-subtext">Size: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
        `;
        
        importBtn.disabled = false;
        importBtn.textContent = 'Import Data from ' + file.name;
        
        showUploadSuccess('Excel file selected successfully! Click "Import Data" to process.');
    } else {
        showUploadError('Please select a valid Excel file (.xlsx or .xls)');
        importBtn.disabled = true;
    }
}

function isValidExcelFile(file) {
    const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.ms-excel' // .xls
    ];
    return validTypes.includes(file.type) || file.name.endsWith('.xlsx') || file.name.endsWith('.xls');
}

function importExcelData(file) {
    const importBtn = document.getElementById('importExcel');
    const originalText = importBtn.textContent;
    
    // Show loading state
    importBtn.disabled = true;
    importBtn.innerHTML = '<span class="loading"></span> Processing Excel file...';
    
    showFileProcessing('Processing Excel file, please wait...');

    const formData = new FormData();
    formData.append('excel_file', file);

    fetch('/import_excel', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideFileProcessing();
        
        if (data.success) {
            populateFormWithExcelData(data.data);
            showUploadSuccess(`Successfully imported data for ${data.data.length} student(s)!`);
            
            // Hide excel section after successful import
            const uploadSection = document.getElementById('excelUploadSection');
            const toggleBtn = document.getElementById('toggleExcelUpload');
            uploadSection.style.display = 'none';
            toggleBtn.textContent = '📊 Import from Excel';
            toggleBtn.classList.remove('btn-secondary');
            toggleBtn.classList.add('btn-primary');
            
        } else {
            showUploadError('Error importing Excel file: ' + data.message);
        }
    })
    .catch(error => {
        hideFileProcessing();
        showUploadError('Error processing file: ' + error.message);
        console.error('Excel import error:', error);
    })
    .finally(() => {
        importBtn.disabled = false;
        importBtn.textContent = originalText;
    });
}

function populateFormWithExcelData(studentsData) {
    if (studentsData.length === 0) return;
    
    // For now, populate with the first student's data
    // Later we can add functionality to handle multiple students
    const studentData = studentsData[0];
    
    // Populate student information
    document.getElementById('student_name').value = studentData.student_name || '';
    document.getElementById('roll_no').value = studentData.roll_no || '';
    document.getElementById('branch').value = studentData.branch || '';
    document.getElementById('semester').value = studentData.semester || '';
    document.getElementById('exam_type').value = studentData.exam_type || '';
    
    // Clear existing subjects
    const subjectsContainer = document.getElementById('subjectsContainer');
    subjectsContainer.innerHTML = '';
    
    // Add subjects from Excel
    studentData.subjects.forEach((subject, index) => {
        const subjectRow = createSubjectRow();
        subjectRow.querySelector('input[name="subject_name[]"]').value = subject.name;
        subjectRow.querySelector('input[name="marks[]"]').value = subject.marks;
        subjectRow.querySelector('input[name="max_marks[]"]').value = subject.max_marks || 100;
        
        subjectsContainer.appendChild(subjectRow);
    });
    
    // Update calculations
    updateMarksCalculation();
    
    // If multiple students, show option to process them all
    if (studentsData.length > 1) {
        showMultipleStudentsOption(studentsData);
    }
}

function showMultipleStudentsOption(studentsData) {
    const notification = document.createElement('div');
    notification.className = 'file-success';
    notification.innerHTML = `
        <div class="success-text">
            Found ${studentsData.length} students in Excel file. Currently showing data for: ${studentsData[0].student_name}
        </div>
        <div style="margin-top: 1rem; text-align: center;">
            <button type="button" class="btn-primary" onclick="processBulkStudents()">
                Process All ${studentsData.length} Students
            </button>
        </div>
    `;
    
    const uploadSection = document.getElementById('excelUploadSection');
    uploadSection.appendChild(notification);
    
    // Store data for bulk processing
    window.bulkStudentsData = studentsData;
}

function processBulkStudents() {
    if (!window.bulkStudentsData) return;
    
    // Redirect to bulk processing page or handle bulk creation
    const confirmation = confirm(`This will create marksheets for all ${window.bulkStudentsData.length} students. Continue?`);
    
    if (confirmation) {
        fetch('/bulk_create_marksheets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                students: window.bulkStudentsData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Successfully created marksheets for ${data.created_count} students!`);
                window.location.href = '/history';
            } else {
                alert('Error creating bulk marksheets: ' + data.message);
            }
        })
        .catch(error => {
            alert('Error processing bulk students: ' + error.message);
        });
    }
}

function downloadExcelTemplate() {
    // Create a sample Excel template
    const templateData = [
        ['Student Name', 'Roll Number', 'Branch', 'Semester', 'Exam Type', 'Mathematics', 'Physics', 'Chemistry', 'Computer Science', 'English'],
        ['John Doe', '2023001', 'Computer Science Engineering', '4th Semester', 'Final Examination', '85', '92', '78', '88', '90'],
        ['Jane Smith', '2023002', 'Information Technology', '4th Semester', 'Final Examination', '88', '85', '92', '90', '87'],
        ['Bob Johnson', '2023003', 'Electronics & Communication', '4th Semester', 'Final Examination', '75', '80', '85', '82', '88']
    ];
    
    // Convert to CSV for download
    const csvContent = templateData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'marksheet_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showUploadSuccess('Template downloaded successfully! Fill it with your data and upload.');
}

function showFileProcessing(message) {
    hideAllUploadMessages();
    const uploadArea = document.querySelector('.upload-area');
    const processingDiv = document.createElement('div');
    processingDiv.className = 'file-processing';
    processingDiv.style.display = 'block';
    processingDiv.innerHTML = `<div class="processing-text">${message}</div>`;
    uploadArea.appendChild(processingDiv);
}

function hideFileProcessing() {
    const processingDiv = document.querySelector('.file-processing');
    if (processingDiv) {
        processingDiv.remove();
    }
}

function showUploadSuccess(message) {
    hideAllUploadMessages();
    const uploadArea = document.querySelector('.upload-area');
    const successDiv = document.createElement('div');
    successDiv.className = 'file-success';
    successDiv.innerHTML = `<div class="success-text">${message}</div>`;
    uploadArea.appendChild(successDiv);
    
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.remove();
        }
    }, 5000);
}

function showUploadError(message) {
    hideAllUploadMessages();
    const uploadArea = document.querySelector('.upload-area');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'file-error';
    errorDiv.innerHTML = `<div class="error-text">${message}</div>`;
    uploadArea.appendChild(errorDiv);
    
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

function hideAllUploadMessages() {
    const messages = document.querySelectorAll('.file-processing, .file-success, .file-error');
    messages.forEach(msg => msg.remove());
}

// Mobile Menu Functionality
function initializeMobileMenu() {
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuButton && navMenu) {
        mobileMenuButton.addEventListener('click', function() {
            const isActive = mobileMenuButton.classList.contains('active');
            
            if (isActive) {
                mobileMenuButton.classList.remove('active');
                navMenu.classList.remove('active');
            } else {
                mobileMenuButton.classList.add('active');
                navMenu.classList.add('active');
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !navMenu.contains(event.target)) {
                mobileMenuButton.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
        
        // Close menu when window is resized to desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                mobileMenuButton.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }
}

// Enhanced Form Animations
function enhanceFormAnimations() {
    const formGroups = document.querySelectorAll('.form-group');
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        },
        { threshold: 0.1 }
    );
    
    formGroups.forEach((group) => {
        observer.observe(group);
    });
}

// Button Loading States
function setButtonLoading(button, isLoading = true) {
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = 'Loading...';
    } else {
        button.classList.remove('loading');
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

// Enhanced Analytics Functions for Dashboard
function initializeAnalytics() {
    loadPerformanceMetrics();
    loadTopPerformers();
    initializePerformersFilters();
}

function loadPerformanceMetrics() {
    fetch('/api/performance_metrics')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPerformanceMetrics(data.metrics);
            }
        })
        .catch(error => console.error('Error loading performance metrics:', error));
}

function displayPerformanceMetrics(metrics) {
    const metricsContainer = document.querySelector('.performance-metrics');
    if (!metricsContainer) return;
    
    metricsContainer.innerHTML = `
        <div class="metric-card excellent">
            <div class="metric-header">
                <span class="metric-title">Excellent (A+/A)</span>
                <span class="metric-icon">🏆</span>
            </div>
            <div class="metric-value">${metrics.excellent || 0}</div>
            <div class="metric-description">Students with 85%+ marks</div>
        </div>
        
        <div class="metric-card good">
            <div class="metric-header">
                <span class="metric-title">Good (B+/B)</span>
                <span class="metric-icon">👍</span>
            </div>
            <div class="metric-value">${metrics.good || 0}</div>
            <div class="metric-description">Students with 70-84% marks</div>
        </div>
        
        <div class="metric-card average">
            <div class="metric-header">
                <span class="metric-title">Average (C)</span>
                <span class="metric-icon">📊</span>
            </div>
            <div class="metric-value">${metrics.average || 0}</div>
            <div class="metric-description">Students with 55-69% marks</div>
        </div>
        
        <div class="metric-card poor">
            <div class="metric-header">
                <span class="metric-title">Needs Improvement</span>
                <span class="metric-icon">📈</span>
            </div>
            <div class="metric-value">${metrics.poor || 0}</div>
            <div class="metric-description">Students below 55% marks</div>
        </div>
    `;
}

function loadTopPerformers() {
    const filters = getPerformersFilters();
    
    fetch('/api/top_performers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayTopPerformers(data.performers);
        }
    })
    .catch(error => console.error('Error loading top performers:', error));
}

function getPerformersFilters() {
    return {
        branch: document.getElementById('branchFilter')?.value || 'all',
        semester: document.getElementById('semesterFilter')?.value || 'all',
        exam_type: document.getElementById('examTypeFilter')?.value || 'all',
        subject: document.getElementById('subjectFilter')?.value || 'all'
    };
}

function displayTopPerformers(performers) {
    const container = document.querySelector('.performers-grid');
    if (!container) return;
    
    container.innerHTML = performers.map((performer, index) => {
        const rankClass = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : '';
        
        return `
            <div class="performer-card">
                <div class="performer-rank ${rankClass}">
                    #${index + 1} ${index < 3 ? ['🥇', '🥈', '🥉'][index] : ''}
                </div>
                <div class="performer-info">
                    <h4>${performer.name}</h4>
                    <div class="performer-details">
                        <span class="detail-label">Roll:</span>
                        <span class="detail-value">${performer.roll_no}</span>
                        <span class="detail-label">Branch:</span>
                        <span class="detail-value">${performer.branch}</span>
                        <span class="detail-label">Semester:</span>
                        <span class="detail-value">${performer.semester}</span>
                        <span class="detail-label">Exam:</span>
                        <span class="detail-value">${performer.exam_type}</span>
                    </div>
                </div>
                <div class="performer-score">
                    <div class="score-value">${performer.percentage}%</div>
                    <div class="score-label">Overall Score</div>
                </div>
            </div>
        `;
    }).join('');
}

function initializePerformersFilters() {
    const filterElements = document.querySelectorAll('.filter-group select');
    filterElements.forEach(filter => {
        filter.addEventListener('change', loadTopPerformers);
    });
    
    // Initialize tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab
            button.classList.add('active');
            tabContents[index]?.classList.add('active');
            
            // Load appropriate data based on tab
            const tabType = button.dataset.tab;
            loadPerformersData(tabType);
        });
    });
}

function loadPerformersData(type) {
    const filters = getPerformersFilters();
    filters.type = type;
    
    fetch('/api/performers_by_type', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayTopPerformers(data.performers);
        }
    })
    .catch(error => console.error('Error loading performers by type:', error));
}

// Enhanced Dashboard Functions
function showAtRiskStudents() {
    fetch('/api/at_risk_students')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.students.length > 0) {
                displayAtRiskStudents(data.students);
            } else {
                alert('No at-risk students found or unable to fetch data.');
            }
        })
        .catch(error => {
            console.error('Error fetching at-risk students:', error);
            alert('Error fetching at-risk students data.');
        });
}

function displayAtRiskStudents(students) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>⚠️ At-Risk Students (Below 40%)</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="students-list">
                    ${students.map(student => `
                        <div class="student-item">
                            <div class="student-info">
                                <h4>${student.name}</h4>
                                <p>Roll: ${student.roll_no} | Branch: ${student.branch}</p>
                                <p>Semester: ${student.semester} | Exam: ${student.exam_type}</p>
                            </div>
                            <div class="student-score danger">
                                ${student.percentage}%
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="modal-actions">
                    <button class="btn-primary" onclick="exportAtRiskData()">Export List</button>
                    <button class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function analyzePerformance() {
    // Scroll to charts section or show detailed analysis
    const chartsSection = document.querySelector('.charts-grid');
    if (chartsSection) {
        chartsSection.scrollIntoView({ behavior: 'smooth' });
    } else {
        alert('Performance analysis charts are being loaded...');
    }
}

function generateCertificates() {
    fetch('/api/star_performers')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.students.length > 0) {
                const confirmed = confirm(`Generate certificates for ${data.students.length} star performers?`);
                if (confirmed) {
                    // Implement certificate generation logic
                    alert('Certificate generation feature will be implemented soon!');
                }
            } else {
                alert('No star performers found or unable to fetch data.');
            }
        })
        .catch(error => {
            console.error('Error fetching star performers:', error);
            alert('Error fetching star performers data.');
        });
}

function exportAtRiskData() {
    window.open('/api/export_at_risk_students', '_blank');
}

// Enhanced Analytics with Grade Distribution
function updateGradeDistribution(distribution) {
    const container = document.querySelector('.grade-cards-grid');
    if (!container || !distribution) return;
    
    const grades = [
        { key: 'a_plus', name: 'A+', range: '90-100%', icon: '🌟', color: 'excellent' },
        { key: 'a_grade', name: 'A', range: '85-89%', icon: '⭐', color: 'very-good' },
        { key: 'b_plus', name: 'B+', range: '75-84%', icon: '👍', color: 'good' },
        { key: 'b_grade', name: 'B', range: '65-74%', icon: '📈', color: 'average' },
        { key: 'c_grade', name: 'C', range: '55-64%', icon: '📊', color: 'below-average' },
        { key: 'd_grade', name: 'D', range: '40-54%', icon: '⚠️', color: 'poor' },
        { key: 'f_grade', name: 'F', range: '0-39%', icon: '❌', color: 'fail' }
    ];
    
    // Animate grade cards
    grades.forEach((grade, index) => {
        setTimeout(() => {
            const card = container.querySelector(`.grade-card.${grade.color}`);
            if (card) {
                card.style.transform = 'translateY(-5px)';
                setTimeout(() => {
                    card.style.transform = 'translateY(0)';
                }, 200);
            }
        }, index * 100);
    });
}

// Enhanced Performance Metrics with Real-time Updates
function refreshDashboardData() {
    // Show loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<div class="spinner"></div> Refreshing data...';
    document.body.appendChild(loadingIndicator);
    
    Promise.all([
        fetch('/api/performance_metrics'),
        fetch('/api/grade_distribution'),
        fetch('/api/semester_stats')
    ])
    .then(responses => Promise.all(responses.map(r => r.json())))
    .then(([metrics, distribution, semesters]) => {
        // Update dashboard with new data
        if (metrics.success) displayPerformanceMetrics(metrics.data);
        if (distribution.success) updateGradeDistribution(distribution.data);
        if (semesters.success) updateSemesterStats(semesters.data);
    })
    .catch(error => {
        console.error('Error refreshing dashboard:', error);
    })
    .finally(() => {
        loadingIndicator.remove();
    });
}

function updateSemesterStats(stats) {
    const container = document.querySelector('.semester-cards-grid');
    if (!container || !stats) return;
    
    // Add animation to semester cards
    const cards = container.querySelectorAll('.semester-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.transform = 'scale(1.02)';
            setTimeout(() => {
                card.style.transform = 'scale(1)';
            }, 150);
        }, index * 100);
    });
}

// Auto-refresh dashboard every 5 minutes
setInterval(refreshDashboardData, 300000);

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .suggestion-chip {
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .suggestion-chip:hover {
        background: #1d4ed8;
        transform: translateY(-2px);
    }
    
    .suggestions-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .subject-suggestions h4 {
        color: #1e293b;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .loading {
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top: 2px solid white;
        border-radius: 50%;
        width: 16px;
        height: 16px;
        animation: spin 1s linear infinite;
        display: inline-block;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;

document.head.appendChild(style);
