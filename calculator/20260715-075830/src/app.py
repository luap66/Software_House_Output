#!/usr/bin/env python3
"""Calculator web application - US-001: Display and Number Input Foundation.

US-002 implementation adds operator selection functionality for basic calculations.
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler


class CalculatorRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for calculator app."""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = self.get_html_template()
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

    def get_html_template(self):
        """Return the HTML template with calculator UI."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Calculator</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f5f5f5;
}}

.calculator {{
    width: 320px;
    max-width: 95vw;
    background-color: #fff;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    padding: 20px;
}}

.display {{
    width: 100%;
    height: 80px;
    background-color: #f9f9f9;
    border: none;
    border-radius: 10px;
    font-size: 36px;
    text-align: right;
    padding: 20px;
    margin-bottom: 20px;
    color: #333;
}}

.buttons {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}}

button {{
    padding: 24px;
    font-size: 20px;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: background-color 0.15s, transform 0.1s;
}}

button:active {{
    transform: scale(0.98);
}}

.number-btn {{
    background-color: #f0f0f0;
    color: #333;
}}

.number-btn:hover {{
    background-color: #e5e5e5;
}}

.operator-btn {{
    background-color: #ff9500;
    color: white;
}}

.operator-btn:hover {{
    background-color: #ffb24d;
}}

.equals-btn {{
    background-color: #3cd68c;
    color: white;
    grid-column: span 2;
}}

.equals-btn:hover {{
    background-color: #5ce0a1;
}}

.clear-btn {{
    background-color: #ff4d4f;
    color: white;
    grid-column: span 2;
}}

.clear-btn:hover {{
    background-color: #ff787c;
}}

button:focus {{
    outline: none;
}}
</style>
</head>
<body>
<div class="calculator">
<input type="text" id="display" class="display" value="" readonly aria-label="Calculator display">
<div class="buttons">
<button class="number-btn" data-value="0" onclick="updateDisplay('0')">0</button>
<button class="number-btn" data-value="1" onclick="updateDisplay('1')">1</button>
<button class="number-btn" data-value="2" onclick="updateDisplay('2')">2</button>
<button class="number-btn" data-value="3" onclick="updateDisplay('3')">3</button>
<button class="number-btn" data-value="4" onclick="updateDisplay('4')">4</button>
<button class="number-btn" data-value="5" onclick="updateDisplay('5')">5</button>
<button class="number-btn" data-value="6" onclick="updateDisplay('6')">6</button>
<button class="number-btn" data-value="7" onclick="updateDisplay('7')">7</button>
<button class="number-btn" data-value="8" onclick="updateDisplay('8')">8</button>
<button class="number-btn" data-value="9" onclick="updateDisplay('9')">9</button>
<button class="operator-btn clear-btn" onclick="clearDisplay()">C</button>
<button class="equals-btn operator-btn" onclick="deleteLastChar()">DEL</button>
<button class="number-btn" data-value="+" onclick="selectOperator('+')">+</button>
<button class="number-btn" data-value="-" onclick="selectOperator('-')">-</button>
<button class="number-btn" data-value="*" onclick="selectOperator('*')">*</button>
<button class="number-btn" data-value="/" onclick="selectOperator('/')">/</button>
</div>
</div>

<script>
(function() {{
    const display = document.getElementById('display');
    
    // Store the selected operator for later calculation
    let pendingOperator = null;
    let firstNumberEntered = false;
    
    function updateDisplay(value) {{
        // Limit to 12 digits as per acceptance criteria
        if (display.value.length >= 12 && value !== '0') {{
            return;
        }}
        
        // If display is empty and user enters a number, start fresh
        if (display.value === '') {{
            display.value = value;
            firstNumberEntered = true;
        }} else {{
            // Append the digit to current display
            display.value += value;
        }}
    }}

    function clearDisplay() {{
        display.value = '';
        pendingOperator = null;
        firstNumberEntered = false;
    }}

    function deleteLastChar() {{
        if (display.value.length > 0) {{
            display.value = display.value.slice(0, -1);
            
            // If display is empty after deletion and we have a pending operator, clear it
            if (!firstNumberEntered && pendingOperator !== null) {{
                pendingOperator = null;
            }} else if (display.value === '' && firstNumberEntered) {{
                firstNumberEntered = false;
            }}
        }}
    }}

    function selectOperator(op) {{
        // Store the selected operator without executing immediately
        if (display.value !== '') {{
            // Replace any existing operators in display to prevent malformed expressions like "5 + -"
            const cleanValue = display.value.replace(/[\s+\-*/]/g, '').trim();
            pendingOperator = op;
            display.value = cleanValue + ' ' + op;
        }} else {{
            // No number yet - just store the operator for when user enters first number
            pendingOperator = op;
        }}
    }}

    function calculateResult() {{
        const expression = display.value.trim();
        
        if (!expression || !pendingOperator) {{
            return '';
        }}
        
        // Parse numbers and operator from the expression
        let num1, num2;
        
        try {{
            // Extract first number (before operator)
            const parts = expression.split(/[\s+\-*/]/);
            
            if (parts.length < 2 || !parts[0] || !parts[1]) {{
                return '';
            }}
            
            num1 = parseFloat(parts[0]);
            let opStr = pendingOperator;
            
            // Handle the operator in parts array
            const remainingParts = expression.split(opStr).map(s => s.trim());
            
            if (remainingParts.length >= 2) {{
                num2 = parseFloat(remainingParts[1]);
                
                // Perform calculation based on selected operator
                let result;
                switch (opStr) {{
                    case '+':
                        result = num1 + num2;
                        break;
                    case '-':
                        result = num1 - num2;
                        break;
                    case '*':
                        result = num1 * num2;
                        break;
                    case '/':
                        if (num2 === 0) {{
                            return 'Error: Division by zero';
                        }}
                        result = num1 / num2;
                        break;
                }}
                
                // Format the result to avoid long decimals
                display.value = parseFloat(result).toString();
            }} else {{
                return '';
            }}
        }} catch (e) {{
            display.value = 'Error';
        }}
        
        // Reset state after calculation - clear pending operator and first number flag
        pendingOperator = null;
        firstNumberEntered = false;
    }}

    function handleEquals() {{
        calculateResult();
    }}

    // Prevent default button behavior and handle clicks via onclick attributes
}})();</script>
</body>
</html>"""


def main():
    """Start the calculator server."""
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, CalculatorRequestHandler)
    
    print(f"Calculator app running at http://localhost:{port}")
    # Note: 0.0.0.0 is the bind address; localhost:<port> for user access
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
