#!/usr/bin/env python

import sys
import os
import shutil
import subprocess
import signal
import http.server
import socketserver
import json

pid_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vlc_server.pid')
port = 8889
version = '0.0.1'

class MyServer(http.server.BaseHTTPRequestHandler):
    def _pid_file_exists(self):
        return os.path.isfile(pid_file)

    def _get_vlc_bin(self):
        vlc_bin = shutil.which('cvlc')
        if vlc_bin is None:
            sys.exit("Couldn't find VLC.")
        return vlc_bin

    def _send_headers(self, code):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

    def _send_obj(self, obj):
        self._send_headers(200)
        self.wfile.write(bytes(json.dumps(obj), 'utf-8'))

    def _send_error(self, code, msg):
        self._send_headers(code)
        self.wfile.write(bytes(json.dumps({'error': msg }), 'utf-8'))

    def _stop_playing(self):
        if not self._pid_file_exists():
            return False

        with open(pid_file, 'r') as handle:
            pid = int(handle.read())
            print('Stopping process %d...' % pid)
            os.kill(pid, signal.SIGTERM)

        return True

    def _play(self, url):
        vlc_bin = self._get_vlc_bin()

        self._stop_playing()

        # Not working, need to adjust this
        cmd = [
                vlc_bin,
                '-q', # quiet
                '-d', # daemon
                '--pidfile', pid_file, # pid file
                url
                ]

        subprocess.run(cmd, stdout=None, stderr=None)

        self._send_obj({'data': url})

    def _stop(self):
        self._send_obj({'status': 'OK', 'result': self._stop_playing()})

    def do_GET(self):
        if self._pid_file_exists():
            status = 'running'
        else:
            status = 'waiting'

        self._send_obj({
                'server': 'screencast-server',
                'version': version,
                'status' : status
            })

    def do_POST(self):
        try:
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        except json.JSONDecodeError:
            self._send_error(400, 'Invalid request')
            return
        except:
            self._send_error(500, 'Server error')
            return

        if not 'action' in data:
            self._send_error(400, 'Missing action')
            return

        action = data['action']

        if action == 'play':
            if 'url' in data:
                self._play(data['url'])
            else:
                self._send_error(400, 'Missing URL')
        elif action == 'stop':
            self._stop()
        else:
            self._send_error(400, 'Invalid action')

with socketserver.TCPServer(('', port), MyServer) as httpd:
    print('Serving at port ', port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()

    print('Server stopped')

# def start_listening():
#     if pid_file_exists():
#         sys.exit('Already running.')
#
#     host, port = pick_random_port()
#     url = build_stream_url(host, port)
#
#     cmd = [
#             vlc_bin,
#             '-q', # quiet
#             '-d', # daemon
#             '--pidfile', pid_file, # pid file
#             '-vvv', 'screen://', ':screen-fps=15',
#             '--sout=#transcode{vcodec=h264,acodec=none,fps=15}:rtp{dst=%s,port=%s,mux=ts,ttl=1,sdp=%s}'  % (host, port, url)
#             ]
#
#     subprocess.run(cmd, stdout=None, stderr=None)
#
#     print('Serving at %s...' % url)
#

def main():
    """Start listening for URLs"""

if __name__ == '__main__':
    main()

