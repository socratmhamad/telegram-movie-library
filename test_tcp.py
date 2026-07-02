import socket
import struct
import time

def test_pg_ssl_request():
    host = "dpg-d9373snaqgkc73cbu87g-a.virginia-postgres.render.com"
    port = 5432
    print(f"Connecting to {host}:{port}")
    # No timeout
    s = socket.create_connection((host, port))
    print("TCP connection established. Sending SSLRequest...")
    
    ssl_req = struct.pack('!II', 8, 80877103)
    s.sendall(ssl_req)
    
    t0 = time.time()
    try:
        resp = s.recv(1)
        if not resp:
            print(f"Server closed connection after {time.time() - t0:.2f}s")
        else:
            print(f"Server responded: {resp} after {time.time() - t0:.2f}s")
    except Exception as e:
        print(f"Exception after {time.time() - t0:.2f}s: {e}")
        
    s.close()

if __name__ == '__main__':
    test_pg_ssl_request()
