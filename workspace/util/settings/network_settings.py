from db_params import computer

def check_port():
    # check if port is open
    from os import system
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 27018))
    if result != 0: print('opening port'); system(f"ssh -N -f -L 27018:127.0.0.1:27017 {computer['hostname']}@{computer['ip']}")
check_port()