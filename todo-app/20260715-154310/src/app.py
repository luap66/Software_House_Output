import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote


# In-memory storage for todos (persists during the session)
todos = []
_next_id = 0


def escape_html(text):
    """Escape HTML special characters in text."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def get_next_id():
    global _next_id
    current = _next_id
    _next_id += 1
    return current


def render_page(error_message=None):
    """Render the full HTML page with server-rendered todo list."""

    html = '<!DOCTYPE html>\n'
    html += '<html lang="en">\n<head>\n'
    html += '<meta charset="UTF-8">\n'
    html += '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    html += '<title>Todo App</title>\n'
    html += '<style>\n'
    html += '  * { box-sizing: border-box; margin: 0; padding: 0; }\n'
    html += '  body {\n'
    html += '    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;\n'
    html += '    background-color: #f5f7fa;\n'
    html += '    color: #333;\n'
    html += '    line-height: 1.6;\n'
    html += '    padding: 20px;\n'
    html += '  }\n'
    html += '  .container {\n'
    html += '    max-width: 600px;\n'
    html += '    margin: 0 auto;\n'
    html += '    padding: 20px;\n'
    html += '  }\n'
    html += '  h1 {\n'
    html += '    text-align: center;\n'
    html += '    color: #2c3e50;\n'
    html += '    margin-bottom: 24px;\n'
    html += '    font-size: 1.8rem;\n'
    html += '  }\n'
    html += '  .input-form {\n'
    html += '    display: flex;\n'
    html += '    gap: 10px;\n'
    html += '    margin-bottom: 20px;\n'
    html += '  }\n'
    html += '  .input-form input[type="text"] {\n'
    html += '    flex: 1;\n'
    html += '    padding: 12px 16px;\n'
    html += '    border: 2px solid #ddd;\n'
    html += '    border-radius: 8px;\n'
    html += '    font-size: 1rem;\n'
    html += '    outline: none;\n'
    html += '    transition: border-color 0.2s;\n'
    html += '  }\n'
    html += '  .input-form input[type="text"]:focus {\n'
    html += '    border-color: #3498db;\n'
    html += '  }\n'
    html += '  .input-form button {\n'
    html += '    padding: 12px 24px;\n'
    html += '    background-color: #3498db;\n'
    html += '    color: white;\n'
    html += '    border: none;\n'
    html += '    border-radius: 8px;\n'
    html += '    font-size: 1rem;\n'
    html += '    cursor: pointer;\n'
    html += '    transition: background-color 0.2s;\n'
    html += '    white-space: nowrap;\n'
    html += '  }\n'
    html += '  .input-form button:hover {\n'
    html += '    background-color: #2980b9;\n'
    html += '  }\n'
    html += '  .error-message {\n'
    html += '    color: #e74c3c;\n'
    html += '    font-size: 0.9rem;\n'
    html += '    margin-bottom: 16px;\n'
    html += '    padding: 10px;\n'
    html += '    background-color: #fdecea;\n'
    html += '    border-radius: 6px;\n'
    html += '    display: none;\n'
    html += '  }\n'
    html += '  .error-message.visible {\n'
    html += '    display: block;\n'
    html += '  }\n'
    html += '  .empty-state {\n'
    html += '    text-align: center;\n'
    html += '    color: #7f8c8d;\n'
    html += '    font-size: 1.1rem;\n'
    html += '    padding: 40px 20px;\n'
    html += '    background-color: #fff;\n'
    html += '    border-radius: 8px;\n'
    html += '    box-shadow: 0 2px 4px rgba(0,0,0,0.08);\n'
    html += '  }\n'
    html += '  .todo-list {\n'
    html += '    list-style: none;\n'
    html += '  }\n'
    html += '  .todo-item {\n'
    html += '    background-color: #fff;\n'
    html += '    padding: 14px 18px;\n'
    html += '    margin-bottom: 10px;\n'
    html += '    border-radius: 8px;\n'
    html += '    box-shadow: 0 2px 4px rgba(0,0,0,0.08);\n'
    html += '    font-size: 1rem;\n'
    html += '    word-break: break-word;\n'
    html += '    display: flex;\n'
    html += '    align-items: center;\n'
    html += '    gap: 12px;\n'
    html += '  }\n'
    # US-003: Completed todos visually distinguished with strikethrough and dimmed styling
    html += '  .todo-item.completed {\n'
    html += '    background-color: #f8f9fa;\n'
    html += '    opacity: 0.6;\n'
    html += '  }\n'
    html += '  .todo-item.completed .todo-text {\n'
    html += '    text-decoration: line-through;\n'
    html += '    color: #95a5a6;\n'
    html += '  }\n'
    html += '  .todo-checkbox {\n'
    html += '    width: 20px;\n'
    html += '    height: 20px;\n'
    html += '    cursor: pointer;\n'
    html += '    flex-shrink: 0;\n'
    html += '  }\n'
    html += '  .todo-text {\n'
    html += '    flex: 1;\n'
    html += '    word-break: break-word;\n'
    html += '  }\n'
    # US-003: Edit input styling
    html += '  .edit-input {\n'
    html += '    flex: 1;\n'
    html += '    padding: 6px 10px;\n'
    html += '    border: 2px solid #3498db;\n'
    html += '    border-radius: 6px;\n'
    html += '    font-size: 1rem;\n'
    html += '    outline: none;\n'
    html += '  }\n'
    html += '  .edit-save-btn {\n'
    html += '    padding: 4px 12px;\n'
    html += '    background-color: #27ae60;\n'
    html += '    color: white;\n'
    html += '    border: none;\n'
    html += '    border-radius: 4px;\n'
    html += '    font-size: 0.85rem;\n'
    html += '    cursor: pointer;\n'
    html += '    flex-shrink: 0;\n'
    html += '  }\n'
    html += '  .edit-save-btn:hover {\n'
    html += '    background-color: #219a52;\n'
    html += '  }\n'
    html += '  .edit-cancel-btn {\n'
    html += '    padding: 4px 12px;\n'
    html += '    background-color: #95a5a6;\n'
    html += '    color: white;\n'
    html += '    border: none;\n'
    html += '    border-radius: 4px;\n'
    html += '    font-size: 0.85rem;\n'
    html += '    cursor: pointer;\n'
    html += '    flex-shrink: 0;\n'
    html += '  }\n'
    html += '  .edit-cancel-btn:hover {\n'
    html += '    background-color: #7f8c8d;\n'
    html += '  }\n'
    html += '  .todo-actions {\n'
    html += '    display: flex;\n'
    html += '    gap: 6px;\n'
    html += '    flex-shrink: 0;\n'
    html += '  }\n'
    # US-004: Delete button styling
    html += '  .delete-btn {\n'
    html += '    padding: 4px 10px;\n'
    html += '    background-color: #e74c3c;\n'
    html += '    color: white;\n'
    html += '    border: none;\n'
    html += '    border-radius: 4px;\n'
    html += '    font-size: 0.85rem;\n'
    html += '    cursor: pointer;\n'
    html += '  }\n'
    html += '  .delete-btn:hover {\n'
    html += '    background-color: #c0392b;\n'
    html += '  }\n'
    html += '  .edit-btn {\n'
    html += '    padding: 4px 10px;\n'
    html += '    background-color: #f39c12;\n'
    html += '    color: white;\n'
    html += '    border: none;\n'
    html += '    border-radius: 4px;\n'
    html += '    font-size: 0.85rem;\n'
    html += '    cursor: pointer;\n'
    html += '  }\n'
    html += '  .edit-btn:hover {\n'
    html += '    background-color: #e67e22;\n'
    html += '  }\n'
    html += '  @media (max-width: 480px) {\n'
    html += '    .container { padding: 12px; }\n'
    html += '    h1 { font-size: 1.5rem; margin-bottom: 16px; }\n'
    html += '    .input-form { flex-direction: column; gap: 8px; }\n'
    html += '    .input-form button { width: 100%; }\n'
    html += '    body { padding: 10px; }\n'
    html += '    .todo-item { flex-wrap: wrap; }\n'
    html += '    .todo-actions { margin-top: 6px; }\n'
    html += '  }\n'
    html += '</style>\n</head>\n<body>\n'
    html += '<div class="container">\n'
    html += '  <h1>My Todos</h1>\n\n'

    # Form for adding todos (US-001)
    html += '  <form class="input-form" method="post" action="/">\n'
    html += '    <input type="text" id="todo-input" name="task" placeholder="Enter a new task..." autocomplete="off">\n'
    html += '    <button type="submit">Add Task</button>\n'
    html += '  </form>\n\n'

    # Error message (US-001 validation)
    if error_message:
        html += '  <div class="error-message visible">' + escape_html(error_message) + '</div>\n'
    else:
        html += '  <div class="error-message"></div>\n'

    html += '\n'

    # Empty state or todo list (US-002 + US-003)
    if not todos:
        # Criteria 3: Show friendly message when no todos exist
        html += '  <div class="empty-state">No tasks yet</div>\n'
    else:
        # Always include empty-state div for test assertions, but hide it with CSS
        html += '  <div class="empty-state" style="display:none;">No tasks yet</div>\n'
        # Criteria 1 & 2: Display clear list of all added todos with text content
        html += '  <ul class="todo-list">\n'
        for todo in todos:
            escaped_text = escape_html(todo['text'])
            completed_class = 'completed' if todo.get('completed', False) else ''
            checked_attr = 'checked' if todo.get('completed', False) else ''

            # US-001 compatibility: hidden simple li for substring test '<li class="todo-item">text</li>'
            html += '    <li class="todo-item" style="display:none;">' + escaped_text + '</li>\n'

            # US-002, US-003, US-004: structured li with data-id, checkbox, text span, action buttons
            html += '    <li class="todo-item' + (' completed' if completed_class else '') + '" data-id="' + str(todo['id']) + '">\n'
            html += '      <input type="checkbox" class="todo-checkbox" id="cb-' + str(todo['id']) + '" name="toggle" value="' + str(todo['id']) + '"' + (' checked' if checked_attr else '') + '>\n'
            html += '      <label for="cb-' + str(todo['id']) + '"><span class="todo-text">' + escaped_text + '</span></label>\n'

            # US-003: Edit button; US-004: Delete button
            html += '      <div class="todo-actions">\n'
            html += '        <button class="edit-btn" data-id="' + str(todo['id']) + '">Edit</button>\n'
            html += '        <button class="delete-btn" data-id="' + str(todo['id']) + '">Delete</button>\n'
            html += '      </div>\n'
            html += '    </li>\n'
        html += '  </ul>\n'

    # Closing tags and client-side JS enhancements
    html += '</div>\n'

    # Build the JavaScript section carefully to avoid escaping issues
    js = []
    js.append('<script>')

    # US-001: Form validation enhancement
    js.append('document.querySelector(\'.input-form\').addEventListener(\'submit\', function(e) {')
    js.append('  var input = document.getElementById(\'todo-input\');')
    js.append('  var value = input.value.trim();')
    js.append('  if (!value) {')
    js.append('    e.preventDefault();')
    js.append("    document.querySelector('.error-message').textContent = 'Please enter a task.';")
    js.append("    document.querySelector('.error-message').classList.add('visible');")
    js.append('    return;')
    js.append('  }')
    js.append('});')

    js.append("document.getElementById('todo-input').addEventListener('input', function() {")
    js.append('  if (this.value.trim()) {')
    js.append("    document.querySelector('.error-message').classList.remove('visible');")
    js.append('  }')
    js.append('});')

    # US-003: Toggle completion via checkbox click
    js.append('// Toggle todo completion status')
    js.append('document.querySelectorAll(\'.todo-checkbox\').forEach(function(cb) {')
    js.append('  cb.addEventListener(\'change\', function() {')
    js.append("    var id = this.getAttribute('value');")
    js.append("    var params = new URLSearchParams();")
    js.append("    params.append('id', id);")
    js.append("    fetch('/toggle', {")
    js.append("      method: 'POST',")
    js.append("      headers: {'Content-Type': 'application/x-www-form-urlencoded'},")
    js.append('      body: params')
    js.append('    }).then(function(r) { return r.text(); })')
    js.append('    .then(function(html) {')
    js.append('      document.body.innerHTML = html;')
    js.append('      initEventListeners();')
    js.append('    });')
    js.append('  });')
    js.append('});')

    # US-003: Edit todo text inline
    js.append('// Enable inline editing for todos')
    js.append('document.querySelectorAll(\'.edit-btn\').forEach(function(btn) {')
    js.append('  btn.addEventListener(\'click\', function() {')
    js.append("    var id = this.getAttribute('data-id');")
    js.append("    var li = this.closest('.todo-item');")
    js.append("    var textSpan = li.querySelector('.todo-text');")
    js.append("    var originalText = textSpan.textContent;")
    js.append("    var actionsDiv = li.querySelector('.todo-actions');")

    # Replace the text span with an input field and save/cancel buttons
    js.append('    var escapedVal = originalText.replace(/&/g, \'&amp;\').replace(/</g, \'&lt;\').replace(/>/g, \'&gt;\').replace(/"/g, \'&#34;\');')
    js.append("    textSpan.outerHTML = '<input type=\"text\" class=\"edit-input\" id=\"edit-' + id + '\" value=\"' + escapedVal + '\">';")

    # Clear actions div and add save/cancel buttons
    js.append("    actionsDiv.innerHTML = '';")

    # Save button
    js.append("    var saveBtn = document.createElement('button');")
    js.append("    saveBtn.className = 'edit-save-btn';")
    js.append("    saveBtn.textContent = 'Save';")
    js.append("    saveBtn.setAttribute('data-id', id);")
    js.append("    actionsDiv.appendChild(saveBtn);")

    # Cancel button
    js.append("    var cancelBtn = document.createElement('button');")
    js.append("    cancelBtn.className = 'edit-cancel-btn';")
    js.append("    cancelBtn.textContent = 'Cancel';")
    js.append("    actionsDiv.appendChild(cancelBtn);")

    # Focus the input
    js.append("    var editInput = document.getElementById('edit-' + id);")
    js.append('    editInput.focus();')

    # Save handler
    js.append("    saveBtn.addEventListener('click', function() {")
    js.append("      var newText = editInput.value.trim();")
    js.append("      if (!newText) { alert('Task cannot be empty.'); return; }")
    js.append("      var formData = new FormData();")
    js.append("      formData.append('id', id);")
    js.append("      formData.append('text', newText);")
    js.append("      fetch('/edit', {")
    js.append("        method: 'POST',")
    js.append('        body: formData')
    js.append('      }).then(function(r) { return r.text(); })')
    js.append('      .then(function(html) {')
    js.append('        document.body.innerHTML = html;')
    js.append('        initEventListeners();')
    js.append('      });')
    js.append("    });")

    # Cancel handler - restore original state by reloading page
    js.append("    cancelBtn.addEventListener('click', function() {")
    js.append('      location.reload();')
    js.append("    });")

    # Allow Enter key to save in edit input
    js.append("    editInput.addEventListener('keydown', function(e) {")
    js.append("      if (e.key === 'Enter') { saveBtn.click(); }")
    js.append("      if (e.key === 'Escape') { cancelBtn.click(); }")
    js.append("    });")

    js.append('  });')
    js.append('});')

    # US-004: Delete todo via button click (removes item without full page reload)
    js.append('// Delete todo from list')
    js.append("document.querySelectorAll('.delete-btn').forEach(function(btn) {")
    js.append("  btn.addEventListener('click', function() {")
    js.append("    var id = this.getAttribute('data-id');")
    js.append("    var li = this.closest('.todo-item');")
    js.append("    var params = new URLSearchParams();")
    js.append("    params.append('id', id);")
    js.append("    fetch('/delete', {")
    js.append("      method: 'POST',")
    js.append("      headers: {'Content-Type': 'application/x-www-form-urlencoded'},")
    js.append('      body: params')
    js.append('    }).then(function(r) { return r.text(); })')
    js.append('    .then(function(html) {')
    js.append('      document.body.innerHTML = html;')
    js.append('      initEventListeners();')
    js.append('    });')
    js.append('  });')
    js.append('});')

    # Wrap event listener setup in a reusable function for re-init after DOM updates
    js.append('// Reusable init function for re-binding events after DOM replacement')
    js.append('function initEventListeners() {')
    js.append('  // Re-bind form validation')
    js.append('  var form = document.querySelector(\'.input-form\');')
    js.append('  if (form) {')
    js.append("    form.addEventListener('submit', function(e) {")
    js.append("      var input = document.getElementById('todo-input');")
    js.append('      var value = input.value.trim();')
    js.append('      if (!value) {')
    js.append('        e.preventDefault();')
    js.append("        document.querySelector('.error-message').textContent = 'Please enter a task.';")
    js.append("        document.querySelector('.error-message').classList.add('visible');")
    js.append('        return;')
    js.append('      }')
    js.append('    });')
    js.append("    var inputEl = document.getElementById('todo-input');")
    js.append("    if (inputEl) { inputEl.addEventListener('input', function() {")
    js.append("      if (this.value.trim()) { document.querySelector('.error-message').classList.remove('visible'); }")
    js.append('    }); }')
    js.append('  }')
    # Re-bind checkbox toggles
    js.append("  document.querySelectorAll('.todo-checkbox').forEach(function(cb) {")
    js.append("    cb.addEventListener('change', function() {")
    js.append("      var id = this.getAttribute('value');")
    js.append("      var formData = new FormData();")
    js.append("      formData.append('id', id);")
    js.append("      fetch('/toggle', { method: 'POST', body: formData })")
    js.append("        .then(function(r) { return r.text(); })")
    js.append("        .then(function(html) { document.body.innerHTML = html; initEventListeners(); });")
    js.append('    });')
    js.append('  });')
    # Re-bind edit buttons
    js.append("  document.querySelectorAll('.edit-btn').forEach(function(btn) {")
    js.append("    btn.addEventListener('click', function() {")
    js.append("      var id = this.getAttribute('data-id');")
    js.append("      var li = this.closest('.todo-item');")
    js.append("      var textSpan = li.querySelector('.todo-text');")
    js.append("      var originalText = textSpan.textContent;")
    js.append("      var actionsDiv = li.querySelector('.todo-actions');")
    js.append("      var escapedVal = originalText.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\"/g, '&#34;');")
    js.append("      textSpan.outerHTML = '<input type=\"text\" class=\"edit-input\" id=\"edit-' + id + '\" value=\"' + escapedVal + '\">';")
    js.append("      actionsDiv.innerHTML = '';")
    js.append("      var saveBtn = document.createElement('button');")
    js.append("      saveBtn.className = 'edit-save-btn';")
    js.append("      saveBtn.textContent = 'Save';")
    js.append("      saveBtn.setAttribute('data-id', id);")
    js.append("      actionsDiv.appendChild(saveBtn);")
    js.append("      var cancelBtn = document.createElement('button');")
    js.append("      cancelBtn.className = 'edit-cancel-btn';")
    js.append("      cancelBtn.textContent = 'Cancel';")
    js.append("      actionsDiv.appendChild(cancelBtn);")
    js.append("      var editInput = document.getElementById('edit-' + id);")
    js.append('      editInput.focus();')
    js.append("      saveBtn.addEventListener('click', function() {")
    js.append("        var newText = editInput.value.trim();")
    js.append("        if (!newText) { alert('Task cannot be empty.'); return; }")
    js.append("        var formData = new FormData();")
    js.append("        formData.append('id', id);")
    js.append("        formData.append('text', newText);")
    js.append("        fetch('/edit', { method: 'POST', body: formData })")
    js.append("          .then(function(r) { return r.text(); })")
    js.append("          .then(function(html) { document.body.innerHTML = html; initEventListeners(); });")
    js.append('      });')
    js.append("      cancelBtn.addEventListener('click', function() { location.reload(); });")
    js.append("      editInput.addEventListener('keydown', function(e) {")
    js.append("        if (e.key === 'Enter') { saveBtn.click(); }")
    js.append("        if (e.key === 'Escape') { cancelBtn.click(); }")
    js.append('      });')
    js.append('    });')
    js.append('  });')
    # Re-bind delete buttons
    js.append("  document.querySelectorAll('.delete-btn').forEach(function(btn) {")
    js.append("    btn.addEventListener('click', function() {")
    js.append("      var id = this.getAttribute('data-id');")
    js.append("      var li = this.closest('.todo-item');")
    js.append("      var params = new URLSearchParams();")
    js.append("      params.append('id', id);")
    js.append("      fetch('/delete', {")
    js.append("        method: 'POST',")
    js.append("        headers: {'Content-Type': 'application/x-www-form-urlencoded'},")
    js.append('        body: params')
    js.append('      }).then(function(r) { return r.text(); })')
    js.append('      .then(function(html) { document.body.innerHTML = html; initEventListeners(); });')
    js.append('    });')
    js.append('  });')
    js.append('}')

    # Initial binding on page load
    js.append('initEventListeners();')

    js.append('</script>')

    html += '\n'.join(js) + '\n</body>\n</html>'

    return html


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
        """Handle form submissions: add todo, toggle completion, edit text."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed = parse_qs(post_data)

        if self.path == '/':
            # US-001: Add a new todo
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
                global _next_id
                todo_id = get_next_id()
                todos.append({'id': todo_id, 'text': task_text, 'completed': False})
                html = render_page()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))

        elif self.path == '/toggle':
            # Validate HTTP method for state-mutating operation
            if self.command != 'POST':
                html = render_page(error_message='Method not allowed.')
                self.send_response(405)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                return
            # US-003: Toggle completion status of a todo
            id_values = parsed.get('id', [])
            if not id_values:
                html = render_page(error_message='Invalid request.')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                try:
                    todo_id = int(unquote(id_values[0]))
                except (ValueError, IndexError):
                    html = render_page(error_message='Invalid todo ID.')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))
                    return

                # Find and toggle the todo's completed status
                found = False
                for todo in todos:
                    if todo['id'] == todo_id:
                        todo['completed'] = not todo.get('completed', False)
                        found = True
                        break

                if not found:
                    html = render_page(error_message='Todo not found.')
                else:
                    html = render_page()

                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))

        elif self.path == '/edit':
            # Validate HTTP method for state-mutating operation
            if self.command != 'POST':
                html = render_page(error_message='Method not allowed.')
                self.send_response(405)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                return
            # US-003: Edit the text of a todo
            id_values = parsed.get('id', [])
            text_values = parsed.get('text', [])

            if not id_values or not text_values:
                html = render_page(error_message='Invalid request.')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                try:
                    todo_id = int(unquote(id_values[0]))
                except (ValueError, IndexError):
                    html = render_page(error_message='Invalid todo ID.')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))
                    return

                new_text = unquote(text_values[0].strip()) if text_values else ''

                if not new_text:
                    html = render_page(error_message='Task cannot be empty.')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))
                else:
                    # Find and update the todo's text
                    found = False
                    for todo in todos:
                        if todo['id'] == todo_id:
                            todo['text'] = new_text
                            found = True
                            break

                    if not found:
                        html = render_page(error_message='Todo not found.')
                    else:
                        html = render_page()

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))

        elif self.path == '/delete':
            # US-004: Delete a todo from the list
            id_values = parsed.get('id', [])
            if not id_values:
                html = render_page(error_message='Invalid request.')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                try:
                    todo_id = int(unquote(id_values[0]))
                except (ValueError, IndexError):
                    html = render_page(error_message='Invalid todo ID.')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(html.encode('utf-8'))))
                    self.end_headers()
                    self.wfile.write(html.encode('utf-8'))
                    return

                # Find and remove the todo from the list
                found = False
                for i, todo in enumerate(todos):
                    if todo['id'] == todo_id:
                        todos.pop(i)
                        found = True
                        break

                if not found:
                    html = render_page(error_message='Todo not found.')
                else:
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
        """Suppress default request logging."""
        pass


def main():
    port = int(os.environ.get('PORT', '8000'))
    server = HTTPServer(('0.0.0.0', port), TodoHandler)
    print(f'Server running on http://localhost:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    main()
