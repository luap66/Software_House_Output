import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── HTML Template ────────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Calculator</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #f4f6f8;
      color: #333;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 1rem;
    }}
    .calculator {{
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 4px 24px rgba(0,0,0,.1);
      padding: 2rem;
      width: 100%;
      max-width: 480px;
    }}
    h1 {{ text-align: center; margin-bottom: 1.5rem; font-size: 1.5rem; color: #1a1a2e; }}
    .input-group {{ margin-bottom: 1rem; }}
    label {{ display: block; margin-bottom: .4rem; font-weight: 600; font-size: .9rem; }}
    input[type="number"], select {{
      width: 100%;
      padding: .75rem;
      border: 1px solid #ccc;
      border-radius: 8px;
      font-size: 1rem;
      transition: border-color .2s;
    }}
    input[type="number"]:focus, select:focus {{ border-color: #4a6fa5; outline: none; }}
    button {{
      width: 100%;
      padding: .85rem;
      font-size: 1rem;
      font-weight: 700;
      color: #fff;
      background: #4a6fa5;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background .2s;
    }}
    button:hover {{ background: #3b5998; }}
    .result {{ margin-top: 1.2rem; text-align: center; font-size: 1.1rem; padding: .75rem; border-radius: 8px; }}
    .result.success {{ background: #e6f4ea; color: #1b7a3d; }}
    .result.error   {{ background: #fce8e6; color: #c0392b; }}
    @media (max-width: 520px) {{
      .calculator {{ padding: 1.2rem; }}
      h1 {{ font-size: 1.25rem; }}
    }}
  </style>
</head>
<body>
  <div class="calculator">
    <h1>Calculator</h1>
    <form method="POST" action="/">
      <div class="input-group">
        <label for="num1">Number 1</label>
        <input type="number" id="num1" name="num1" step="any" placeholder="Enter first number"{num1_val}>
      </div>
      <div class="input-group">
        <label for="num2">Number 2</label>
        <input type="number" id="num2" name="num2" step="any" placeholder="Enter second number"{num2_val}>
      </div>
      <div class="input-group">
        <label for="operation">Operation</label>
        <select id="operation" name="operation">
          <option value="add"{opt_add}>Addition (+)</option>
          <option value="subtract"{opt_subtract}>Subtraction (-)</option>
          <option value="multiply"{opt_multiply}>Multiplication (×)</option>
          <option value="divide"{opt_divide}>Division (÷)</option>
        </select>
      </div>
      <button type="submit">Calculate</button>
    </form>
{result_html}
  </div>
</body>
</html>
"""


def build_page(num1="", num2="", operation="add", result=None, error=None):
    """Build the HTML page with server-rendered state."""

    # Input value attributes (server-rendered)
    num1_val = f' value="{num1}"' if num1 else ""
    num2_val = f' value="{num2}"' if num2 else ""

    # Option selected attributes
    opt_add = ' selected' if operation == "add" else ""
    opt_subtract = ' selected' if operation == "subtract" else ""
    opt_multiply = ' selected' if operation == "multiply" else ""
    opt_divide = ' selected' if operation == "divide" else ""

    # Result / error block (server-rendered)
    result_html = ""
    if result is not None:
        result_html = f'<div class="result success"><strong>Result:</strong> {result}</div>'
    elif error:
        result_html = f'<div class="result error">{error}</div>'

    return HTML_TEMPLATE.format(
        num1_val=num1_val,
        num2_val=num2_val,
        opt_add=opt_add,
        opt_subtract=opt_subtract,
        opt_multiply=opt_multiply,
        opt_divide=opt_divide,
        result_html=result_html,
    )


class CalculatorHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "":
            self._serve_page()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            params = parse_qs(body, keep_blank_values=True)

            num1_raw = params.get("num1", [""])[0].strip()
            num2_raw = params.get("num2", [""])[0].strip()
            operation = params.get("operation", ["add"])[0]

            # Validate inputs
            if not num1_raw or not num2_raw:
                html = build_page(
                    num1=num1_raw,
                    num2=num2_raw,
                    operation=operation,
                    error="Please enter both numbers before calculating.",
                )
            else:
                try:
                    a = float(num1_raw)
                    b = float(num2_raw)
                except ValueError:
                    html = build_page(
                        num1=num1_raw,
                        num2=num2_raw,
                        operation=operation,
                        error="Invalid input. Please enter valid numbers.",
                    )
                else:
                    if operation == "add":
                        result = a + b
                    elif operation == "subtract":
                        result = a - b
                    elif operation == "multiply":
                        result = a * b
                    elif operation == "divide":
                        if b == 0:
                            html = build_page(
                                num1=num1_raw,
                                num2=num2_raw,
                                operation=operation,
                                error="Division by zero is not allowed.",
                            )
                            self._send_html(html)
                            return
                        result = a / b
                    else:
                        html = build_page(
                            num1=num1_raw,
                            num2=num2_raw,
                            operation=operation,
                            error="Unknown operation selected.",
                        )
                        self._send_html(html)
                        return

                    # Format result nicely (avoid trailing .0 for whole numbers)
                    if result == int(result):
                        result_str = str(int(result))
                    else:
                        result_str = f"{result:.6f}".rstrip("0").rstrip(".")

                    html = build_page(
                        num1=num1_raw,
                        num2=num2_raw,
                        operation=operation,
                        result=result_str,
                    )

            self._send_html(html)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")

    def _serve_page(self):
        html = build_page()
        self._send_html(html)

    def _send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    # Suppress default request logging to keep output clean
    def log_message(self, format, *args):
        pass


def main():
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), CalculatorHandler)
    print(f"Calculator running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
