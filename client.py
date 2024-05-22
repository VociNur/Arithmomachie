import socket
import time


def client_program():
    host = socket.gethostname()  # as both code is running on same pc
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    
    
    connected = False
    while not connected:
        print("Connecting...")
        try:
            client_socket.connect((host, port))  # connect to the server
            connected = True
        except:
            print("Cannot connect now")
            time.sleep(10)
    print("Connected !")
    
    system = ""
    node_name = ""
    cores_number = ""
    get_os = False
    get_platform = False
    try:
        import os
        cores_number = str(os.cpu_count())
        get_os = True
    except:
        pass

    try:
        import platform
        system_info = platform.uname()
        system = system_info.system
        node_name = system_info.node
        get_platform = True
    except:
        pass

    client_socket.send((system + "," + node_name + "," + cores_number).encode())

    message = ""
    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())  # send message
        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()