#!/usr/bin/env python

import sys
import os
import argparse
import shutil
import netifaces
import socket
import subprocess
import signal

pid_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "vlc.pid")
cast_server = "google.com"
cast_port = 80

def pid_file_exists():
    return os.path.isfile(pid_file)

def get_vlc_bin():
    vlc_bin = shutil.which("cvlc")
    if vlc_bin is None:
        sys.exit("Couldn't find VLC.")
    return vlc_bin

def pick_random_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    host_port = s.getsockname()
    s.close()
    return host_port

def build_stream_url(host, port):
    return "rtsp://%s:%d/" % (host, port)

def start_streaming():
    if pid_file_exists():
        sys.exit("Already running.")

    host, port = pick_random_port()
    vlc_bin = get_vlc_bin()
    url = build_stream_url(host, port)

    cmd = [
            vlc_bin,
            "-q", # quiet
            "-d", # daemon
            "--pidfile", pid_file, # pid file
            "-vvv", "screen://", ":screen-fps=15",
            "--sout=#transcode{vcodec=h264,acodec=none,fps=15}:rtp{dst=%s,port=%s,mux=ts,ttl=1,sdp=%s}"  % (host, port, url)
            ]

    subprocess.run(cmd, stdout=None, stderr=None)

    print("Serving at %s..." % url)

def stop_streaming():
    if not pid_file_exists():
        sys.exit("Not running...")

    with open(pid_file, 'r') as handle:
        pid = int(handle.read())
        print("Stopping process %d..." % pid)
        os.kill(pid, signal.SIGTERM)

def main():
    """This is the main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="Action to do", choices=["start", "stop"])
    args = parser.parse_args()

    if args.action == "start":
        start_streaming()
    elif args.action == "stop":
        stop_streaming()

if __name__ == "__main__":
    main()

