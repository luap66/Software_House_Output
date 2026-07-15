import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import threading


# In-memory todo storage (session-scoped)
todos = []
lock = threading.Lock()


def escape_html(text):
    """Escape special HTML characters to prevent XSS."""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def render_page(current_todos):
    """Server-render the full page with all todos as real HTML elements."""
    items_html = ''
    for i, todo in enumerate(current_todos):
        escaped = escape_html(todo)
        items_html += '<li class="todo-item" data-index="%d"><span class="todo-text">%s</span></li>\n' % (i, escaped)

    if not current_todos:
        items_html = '<li class="empty-message">No tasks yet. Add one above!</li>'

    # Use %-style formatting to avoid conflicts with CSS/JS curly braces
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; display: flex; justify-content: center; padding: 2rem 1rem; }
        .container { max-width: 600px; width: 100%; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 2rem; }
        h1 { text-align: center; color: #333; margin-bottom: 1.5rem; font-size: 1.8rem; }
        .add-form { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
        .add-form input[type="text"] { flex: 1; padding: 0.75rem 1rem; border: 2px solid #ddd; border-radius: 6px; font-size: 1rem; outline: none; transition: border-color 0.2s; }
        .add-form input[type="text"]:focus { border-color: #4a90d9; }
        .add-form button { padding: 0.75rem 1.5rem; background: #4a90d9; color: white; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; transition: background 0.2s; }
        .add-form button:hover { background: #357abd; }
        .todo-list { list-style: none; }
        .todo-item { padding: 0.75rem 1rem; border-bottom: 1px solid #eee; display: flex; align-items: center; }
        .todo-item:last-child { border-bottom: none; }
        .todo-text { color: #333; font-size: 1rem; word-break: break-word; }
        .empty-message { text-align: center; color: #999; padding: 2rem; font-style: italic; }
        @media (max-width: 480px) {
            .container { padding: 1.25rem; }
            h1 { font-size: 1.5rem; }
            .add-form { flex-direction: column; }
            body { padding: 1rem 0.5rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Todo App</h1>
        <form class="add-form" method="POST" action="/">
            <input type="text" name="task" placeholder="Add a new task..." autocomplete="off">
            <button type="submit">Add</button>
        </form>
        <ul class="todo-list">%s</ul>
    </div>
</body>
</html>''' % (items_html,)


class TodoHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Suppress default request logging for cleaner output."""
        pass

    def do_GET(self):
        if self.path == '/':
            with lock:
                snapshot = list(todos)
            html = render_page(snapshot)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        if self.path == '/':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(body)

            task_text = params.get('task', [''])[0].strip()

            # Only add if text is non-empty after stripping whitespace
            added = False
            if task_text:
                with lock:
                    todos.append(task_text)
                added = True

            # POST-Redirect-GET pattern: clears input field on redirect
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(404, 'Not Found')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(('0.0.0.0', port), TodoHandler)
    print(f"Todo app running on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
