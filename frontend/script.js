// DOM elements
const number1Input = document.getElementById('number1');
const number2Input = document.getElementById('number2');
const addButton = document.getElementById('addButton');
const resultDiv = document.getElementById('result');

// API configuration
const API_BASE_URL = 'http://localhost:8000';

// Event listeners
addButton.addEventListener('click', handleAddition);
number1Input.addEventListener('input', validateInput);
number2Input.addEventListener('input', validateInput);
number1Input.addEventListener('keypress', handleKeyPress);
number2Input.addEventListener('keypress', handleKeyPress);

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        handleAddition();
    }
}

// Validate input to ensure only numbers
function validateInput(event) {
    const input = event.target;
    const value = input.value;
    
    // Remove any non-numeric characters except decimal point and minus sign
    const numericValue = value.replace(/[^0-9.-]/g, '');
    
    // Ensure only one decimal point
    const parts = numericValue.split('.');
    if (parts.length > 2) {
        input.value = parts[0] + '.' + parts.slice(1).join('');
    } else {
        input.value = numericValue;
    }
    
    // Update button state
    updateButtonState();
}

// Update add button state based on input validity
function updateButtonState() {
    const num1 = parseFloat(number1Input.value);
    const num2 = parseFloat(number2Input.value);
    
    if (!isNaN(num1) && !isNaN(num2) && number1Input.value.trim() !== '' && number2Input.value.trim() !== '') {
        addButton.disabled = false;
    } else {
        addButton.disabled = true;
    }
}

// Handle addition calculation
async function handleAddition() {
    const num1 = parseFloat(number1Input.value);
    const num2 = parseFloat(number2Input.value);
    
    // Validate inputs
    if (isNaN(num1) || isNaN(num2)) {
        showError('Please enter valid numbers');
        return;
    }
    
    // Disable button during request
    addButton.disabled = true;
    addButton.textContent = 'Calculating...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                number1: num1,
                number2: num2
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showResult(data.result);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to calculate. Please check if the server is running.');
    } finally {
        // Re-enable button
        addButton.disabled = false;
        addButton.textContent = 'Add';
        updateButtonState();
    }
}

// Show calculation result
function showResult(result) {
    resultDiv.textContent = `Result: ${result}`;
    resultDiv.className = 'result show';
}

// Show error message
function showError(message) {
    resultDiv.textContent = message;
    resultDiv.className = 'result show error';
}

// Initialize button state
updateButtonState();
