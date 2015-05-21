#python chat_client localhost [port_num]
import socket, select, string, sys
from getpass import getpass
 
def prompt() :
    sys.stdout.write('<You> ')
    sys.stdout.flush()
 
#main function
if __name__ == "__main__":
     
    if(len(sys.argv) < 3) :
        print ('Usage : python telnet.py hostname port')
        sys.exit()
     
    host = sys.argv[1]
    port = int(sys.argv[2])
    status = 0
    name =''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print ('Unable to connect')
        sys.exit()
     
    print ('Connected to remote host. Start sending messages')
    while 1:
	
        sys.stdout.write('Name:')
        sys.stdout.flush()
        name = sys.stdin.readline()
    	name = name.strip()
    	#print(name)
    	pwd = getpass()
    	#print(name + ',' + pwd)
    	s.send(name + ',' + pwd)
	sys.stdout.flush()
	data = s.recv(4096)
	sys.stdout.flush()
	if data.split('&')[0] == 'you are not member' or data == 'login failed, wrong password' :
		print("login failed")
	elif data.split('&')[0] == 'login success':
		print('login success')
		print(data.split('&')[1])
		status = 1
		break

    #prompt()
    sys.stdout.flush()
    while 1:
        rlist = [sys.stdin, s]

        # Get the list sockets which are readable
        read_list, write_list, error_list = select.select(rlist , [], [])
         
        for sock in read_list:
            #incoming message from remote server
            if sock == s:

                data = sock.recv(4096)
		if not data:
			print ('\nDisconnected from chat server')
			sys.exit()
		if status == 2:
			user = eval(data)
			status=1
			print('------------online user-------------')
			i=0
			for item in user:
				if item != name:
					print(str(i+1) + '.' + item)
			print('------------online user-------------')
		elif status==1:
			#print data
			sys.stdout.write(data)
			sys.stdout.flush()
			#prompt()

             
            #user entered a message
            else :
                msg = sys.stdin.readline()
		#print(msg.strip())
		if msg.strip() == 'listuser':
			status = 2
                s.send(msg)
                #prompt()
		sys.stdout.flush()
		if msg == 'logout':
			s.close()
			sys.exit()
