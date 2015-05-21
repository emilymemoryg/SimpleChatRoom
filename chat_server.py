
import socket, select,sys
 
#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)
		conn_stat.remove(socket)
		index = next(index for (index, d) in enumerate(conn_stat) if d['socket']== socket)
		#print('+++++1')
		#print(conn_stat[index]['name'])
		onlineuser.remove(conn_stat[index]['name'])
 
if __name__ == "__main__":
     
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    conn_stat = []
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
    userlist = [{'name':'merry','pwd':'1234','offline':[]},{'name':'jack','pwd':'1234','offline':[]},{'name':'emily','pwd':'1234','offline':[]}]
    onlineuser = []
     
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

 
    print "Chat server started on port " + str(PORT)
 
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
		conn_stat.append({'socket':sockfd , 'state':0, 'talk':''})
		account = [item for item in conn_stat if item['socket'] == sockfd]
		#if account:
		#    print("yes")
		#    print(str(account[0]['socket']))
		#else:
		#    print("no")
                #print "Client (%s, %s) connected" % addr
                
                #broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
             
            #Some incoming message from a client
	    
            else:
                # Data recieved from client, process it
                try:
		    account = [item for item in conn_stat if item['socket'] == sock]
		    accountindex =  next(index for (index, d) in enumerate(conn_stat) if d['socket']== sock)
		    #if account:
		    #	print(str(account[0]['state']))
		    if account[0]['state'] == 0 :
		    	data = sock.recv(RECV_BUFFER)
			name = data.split(',')[0]
			pwd = data.split(',')[1]
			user = [item for item in userlist if item['name'] == name]
			if user:
				if user[0]['pwd'] == pwd:
					msglist = 'login success&'
					#sys.stdout.flush()
					#print(user[0]['name'] + 'loginsuccess')
					conn_stat[accountindex]['state'] = 1
					conn_stat[accountindex]['name'] = name
					onlineuser.append(user[0]['name'])
					userindex = next(index for (index, d) in enumerate(userlist) if d['name']== name)
					#print('$')
					if userlist[userindex]['offline']:
						for item in userlist[userindex]['offline']:
							msglist += '<message from '+ item['name'] +'>'+item['msg']
					sock.sendall(msglist)
					userlist[userindex]['offline'] = []
					#------------------
					broadcast_data(sockfd,  'Client ' + name +  " login\n" )
					#print(userlist[userindex]['offline'])
				else:
					sock.send('login failed, wrong password&')
					#print('wrong password')
			else:
				sock.send('you are not member&')
				#print(name + ' not member')
		    elif account[0]['state'] == 1:
			data = sock.recv(RECV_BUFFER)
			command = data.split(' ')[0].strip()
			if command == 'listuser':
				#print(onlineuser)
				sock.send(str(onlineuser))
			elif command == 'broadcast':
				if data: 
					#print(account)
					broadcast_data(sock, "\r" + '<' + str(account[0]['name']) + '> ' + data.split(' ')[1]) 
			elif command == 'talk':
				#print(data)
				talkto = [item for item in conn_stat if item['name'] == data.split(' ')[1].strip()]
				#print(data.split(' ')[1])
				conn_stat[accountindex]['talk'] = data.split(' ')[1].strip()
				conn_stat[accountindex]['state'] = 3
				#talktosock = talkto[0]['socket']
				#conn_stat[accountindex]['socket'].send('---------------talk someone--------------')
				#talktosock.send("\r" + "<" + talkto[0]['name'] + "(private)>" + data.split(' ')[2])
			elif command == 'logout':
				index = next(index for (index, d) in enumerate(conn_stat) if d['socket']== sock)
				broadcast_data(sock, 'Client ' + conn_stat[index]['name'] + ' is offline \n')
                    		print ('Client ' + conn_stat[index]['name'] + ' is offline \n')
				sock.close()
				CONNECTION_LIST.remove(sock)
				
				#print('+++++3')
				#print(onlineuser)
				#print(conn_stat[index]['name'])
				onlineuser.remove(conn_stat[index]['name'])
				#print('+++++3?')
		    		del conn_stat[index]
				#print(conn_stat)
		    elif account[0]['state'] == 3:
			data = sock.recv(RECV_BUFFER)
			if data.strip() == 'end':
				conn_stat[accountindex]['talk'] = ''
				conn_stat[accountindex]['state'] = 1
			else:
				#print('------------')
				#print(accountindex)
				#print(conn_stat[accountindex])
				talkto = [item for item in conn_stat if item['name'] == conn_stat[accountindex]['talk']]
				if not talkto :
					userindex = index = next(index for (index, d) in enumerate(userlist) if d['name']== conn_stat[accountindex]['talk'])
					userlist[userindex]['offline'].append({'name':account[0]['name'],'msg':data})
					#print(userlist)
				else:
					talktosock = talkto[0]['socket']
					talktosock.send("\r" + "<" + talkto[0]['name'] + "(private)>" + data)
				
					
		    else:
			#if data == 'listuser'
			#In Windows, sometimes when a TCP program closes abruptly,
                    	# a "Connection reset by peer" exception will be thrown
                    	data = sock.recv(RECV_BUFFER)
                    	if data:
                        	broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)                
                 

                    
                except:
		    index = next(index for (index, d) in enumerate(conn_stat) if d['socket']== sock)
                    broadcast_data(sock, 'Client' + conn_stat[index]['name'] + 'is offline')
                    print ('Client' + conn_stat[index]['name'] + 'is offline')
                    sock.close()
                    CONNECTION_LIST.remove(sock)
		    #conn_stat.remove(sock)
		    
		    del conn_stat[index]
		    #print('+++++2')
		    #print(conn_stat[index]['name'])
	            onlineuser.remove(conn_stat[index]['name'])
		    #print(conn_stat)
                    continue
     
    server_socket.close()
