import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote


# In-memory storage for todos (persists during the session)
todos = []


def render_page(error_message=None):
    """Render the full HTML page with server-rendered todo list."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Todo App</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #f5f7fa;
    color: #333;
    line-height: 1.6;
    padding: 20px;
  }
  .container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }
  h1 {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 24px;
    font-size: 1.8rem;
  }
  .input-form {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
  }
  .input-form input[type="text"] {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s;
  }
  .input-form input[type="text"]:focus {
    border-color: #3498db;
  }
  .input-form button {
    padding: 12px 24px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    white-space: nowrap;
  }
  .input-form button:hover {
    background-color: #2980b9;
  }
  .error-message {
    color: #e74c3c;
    font-size: 0.9rem;
    margin-bottom: 16px;
    padding: 10px;
    background-color: #fdecea;
    border-radius: 6px;
    display: none;
  }
  .error-message.visible {
    display: block;
  }
  .todo-list {
    list-style: none;
  }
  .todo-item {
    background-color: #fff;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    font-size: 1rem;
    word-break: break-word;
  }
  .empty-state {
    text-align: center;
    color: #95a5a6;
    padding: 40px 20px;
    font-style: italic;
    font-size: 1rem;
  }
  @media (max-width: 480px) {
    .container { padding: 12px; }
    h1 { font-size: 1.5rem; margin-bottom: 16px; }
    .input-form { flex-direction: column; gap: 8px; }
    .input-form button { width: 100%; }
    body { padding: 10px; }
  }
</style>
</head>
<body>
<div class="container">
  <h1>My Todos</h1>

  <form class="input-form" method="post" action="/">
    <input type="text" id="todo-input" name="task" placeholder="Enter a new task..." autocomplete="off">
    <button type="submit">Add Task</button>
  </form>

"""
    if error_message:
        html += f'  <div class="error-message visible">{error_message}</div>\n'
    else:
        html += '  <div class="error-message"></div>\n'

    html += '\n'

    if todos:
        html += '  <ul class="todo-list">\n'
        for todo in todos:
            escaped_text = escape_html(todo)
            html += f'    <li class="todo-item">{escaped_text}</li>\n'
        html += '  </ul>\n'
    else:
        html += '  <div class="empty-state">No tasks yet. Add one above!</div>\n'

    html += """
</div>
<script>
document.querySelector('.input-form').addEventListener('submit', function(e) {
  var input = document.getElementById('todo-input');
  var value = input.value.trim();
  if (!value) {
    e.preventDefault();
    document.querySelector('.error-message').textContent = 'Please enter a task.';
    document.querySelector('.error-message').classList.add('visible');
    return;
  }
});

document.getElementById('todo-input').addEventListener('input', function() {
  if (this.value.trim()) {
    document.querySelector('.error-message').classList.remove('visible');
  }
});
</script>
</body>
</html>"""
    return html


def escape_html(text):
    """Escape HTML special characters in text."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


class TodoHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Serve the main page with current todos rendered in HTML."""
        if self.path == '/' or self.path == '/index.html':
            html = render_page()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>404 Not Found</h1></body></html>')

    def do_POST(self):
        """Handle form submission to add a new todo."""
        if self.path == '/' or self.path == '/index.html':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed = parse_qs(post_data)

            task_values = parsed.get('task', [])
            task_text = unquote(task_values[0].strip()) if task_values else ''

            if not task_text:
                html = render_page(error_message='Please enter a task.')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                todos.append(task_text)
                html = render_page()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>404 Not Found</h1></body></html>')

    def log_message(self, format, *args):
        """Suppress default request logging for cleaner output."""
        pass


def main():
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(('0.0.0.0', port), TodoHandler)
    print(f"Todo app running on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
