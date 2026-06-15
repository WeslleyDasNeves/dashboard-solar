import http.server
import socketserver

# Sets the port number (defaults to 8000)
PORT = 8000

# The handler that serves files from the current directory
Handler = http.server.SimpleHTTPRequestHandler

# Creates a TCP server to look for requests
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving HTTP on port {PORT}...")
    # Keeps the script running infinitely
    httpd.serve_forever()
