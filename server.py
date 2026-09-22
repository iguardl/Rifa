#!/usr/bin/env python3
"""Servidor estático local para RIFA.

Por defecto solo escucha en 127.0.0.1: nadie fuera de esta PC puede
siquiera abrir la página. La protección de las acciones de admin
(agregar gente, sortear, borrar) sigue siendo el login de Supabase,
no este servidor -- ver README.md.

Uso:
    python server.py                # solo esta PC, puerto 8787
    python server.py --lan          # visible en tu red local (para que
                                     # la gente vea rifa.html
                                     # desde su celular en el evento)
    python server.py --port 9000
"""
import argparse
import http.server
import socketserver
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        print(f"[rifa] {self.address_string()} - {fmt % args}")


def main():
    ap = argparse.ArgumentParser(description="Servidor local para RIFA")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--lan", action="store_true",
                     help="Exponer en la red local (0.0.0.0) en vez de solo esta PC")
    ap.add_argument("--no-open", action="store_true",
                     help="No abrir el navegador automáticamente")
    args = ap.parse_args()

    host = "0.0.0.0" if args.lan else "127.0.0.1"
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer((host, args.port), Handler) as httpd:
        admin_url = f"http://localhost:{args.port}/admin.html"
        print(f"RIFA admin: {admin_url}")
        if args.lan:
            print("Modo LAN: cualquiera en tu WiFi puede ABRIR la página (incluida la de admin).")
            print("Eso está bien porque sin iniciar sesión en Supabase nadie puede tocar nada,")
            print("pero comparte solo el link de rifa.html con tus invitados.")
        else:
            print("Solo esta PC puede abrir el servidor (127.0.0.1). Para compartir la vista")
            print("pública en el evento, corre: python server.py --lan")
        if not args.no_open:
            webbrowser.open(admin_url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nRIFA detenido.")


if __name__ == "__main__":
    main()
