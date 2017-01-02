'''
Send a submit request to islandviewer via tcp
'''

import os
import glob
import sys
import socket
import json
import base64
import time
from django.conf import settings
import pprint

default_host = settings.ISLANDVIEWER_HOST
default_port = settings.ISLANDVIEWER_PORT
timeout = 120

'''
This is the generic handler, we're passed a structure we'll
encode in to json and send to the backend
'''
def send_action(message, host=default_host, port=default_port):
    try:
        s = connect_to_server(host, port)
    except Exception as e:
        if settings.DEBUG:
            print "Socket error: " +  str(e) + " to " + host + ":" + str(port)
            raise Exception("Socket error: " +  str(e) + " to " + host + ":" + str(port))
        raise Exception("Failure to submit file")

    # One little sanity check to ensure we have an action for the
    # backend
    if 'action' in message:
        json_str = json.dumps(message)
        json_str += "\nEOF\n"
        
        ret = send_message(s, json_str)
        
        decoded_json = json.loads(ret)
        
        if settings.DEBUG:
            print decoded_json
        
        return decoded_json
    
    else:
        if settings.DEBUG:
            print "Error, no action given for: " + json_str
            
        raise Exception("Failure to send message, no action")
         

def send_job(genome_data, genome_format, genome_name, email, ip_addr, user_id = None, host=default_host, port=default_port, **kwargs):
    try:
        s = connect_to_server(host, port)
    except Exception as e:
        if settings.DEBUG:
            print "Socket error: " +  str(e) + " to " + host + ":" + str(port)
            raise Exception("Socket error: " +  str(e) + " to " + host + ":" + str(port))
        raise Exception("Failure to submit file")

    encoded_genome = base64.urlsafe_b64encode(genome_data)

    json_obj = {'action': 'submit', 'genome_name': genome_name,
            'email': email, 'genome_data': encoded_genome,
            'genome_format': genome_format, 'ip_addr': ip_addr }

    if user_id:
        json_obj['owner_id'] = user_id

    try:
        json_obj['ref_accnum'] = kwargs['ref_accnum']
    except:
        pass

    # Add any extra arguments to the call to the backend
    if kwargs:
        for key in kwargs:
            if key in kwargs:
                continue
            json_obj[key] = kwargs[key]

    json_str = json.dumps(json_obj)
    json_str += "\nEOF\n"

    ret = send_message(s, json_str)

    decoded_json = json.loads(ret)

    if settings.DEBUG:
        print decoded_json
    
    return decoded_json

def send_picker(accnum, host=default_host, port=default_port, **kwargs):
    try:
        s = connect_to_server(host, port)
    except Exception as e:
        if settings.DEBUG:
            print "Socket error: " +  str(e) + " to " + host + ":" + str(port)
            raise Exception("Socket error: " +  str(e) + " to " + host + ":" + str(port))
        raise Exception("Failure to submit file")

    json_obj = {'action': 'picker', 'accnum': accnum}
    json_obj.update(kwargs)

    json_str = json.dumps(json_obj)
    json_str += "\nEOF\n"

    ret = send_message(s, json_str)

    decoded_json = json.loads(ret)

#    if settings.DEBUG:
#        print decoded_json
    
    return decoded_json
    

def send_clone(aid, user_id=None, host=default_host, port=default_port, **kwargs):
    try:
        s = connect_to_server(host, port)
    except Exception as e:
        if settings.DEBUG:
            print "Socket error: " +  str(e) + " to " + host + ":" + str(port)
            raise Exception("Socket error: " +  str(e) + " to " + host + ":" + str(port))
        raise Exception("Failure to submit file")

    if user_id:
        kwargs['args'].update({'owner_id': user_id})

    json_obj = {'action': 'clone', 'aid': aid}
    json_obj.update(kwargs)
    
    json_str = json.dumps(json_obj)
    json_str += "\nEOF\n"

    if settings.DEBUG:
        print json_str

    ret = send_message(s, json_str)

    decoded_json = json.loads(ret)

    if settings.DEBUG:
        print decoded_json
    
    return decoded_json
   
def send_notify(aid, email, host=default_host, port=default_port, **kwargs):
    try:
        s = connect_to_server(host, port)
    except Exception as e:
        if settings.DEBUG:
            print "Socket error: " +  str(e) + " to " + host + ":" + str(port)
            raise Exception("Socket error: " +  str(e) + " to " + host + ":" + str(port))
        raise Exception("Failure to submit file")

    json_obj = {'action': 'add_notification', 'aid': aid, 'email': email}
    json_obj.update(kwargs)
    
    json_str = json.dumps(json_obj)
    json_str += "\nEOF\n"

    if settings.DEBUG:
        print json_str

    ret = send_message(s, json_str)

    decoded_json = json.loads(ret)

    if settings.DEBUG:
        print decoded_json
    
    return decoded_json
    

def connect_to_server(host, port):

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        if settings.DEBUG:
            print 'Failed to create socket'
        raise Exception("Socket failure", "Error creating a socket")
    
    if settings.DEBUG: 
        print 'Socket Created'
 
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
    #could not resolve
        if settings.DEBUG:
            print 'Hostname could not be resolved. Exiting'
        raise Exception("Socket failure", "Error, could not resolve host " + host)
 
    #Connect to remote server
    s.connect((remote_ip , port))

    return s

def send_message(s, message):
    
    try:
        s.sendall(message)
    except socket.error:
        if settings.DEBUG:
            print "Send failed"
        raise Exception("Socket failure", "Error sending message to server")

    #Now receive data
#    reply = s.recv(4096)
    try:
        reply = recv_timeout(s,timeout)
    except Exception as e:
        if settings.DEBUG:
            print e
        raise e

    return reply

def recv_timeout(the_socket,timeout=2):
    the_socket.setblocking(0)
    total_data=[];data='';begin=time.time()
    while 1:
        # If we've received data, see if the connection has been closed
        # yes not proper socket programming, but it fits the protocol we 
        # already made
        if total_data:
            try:
                the_socket.send('ping')
            except Exception as e:
                if settings.DEBUG:
                    print e
                return ''.join(total_data)
        #if you got some data, then break after wait sec
        elif total_data and time.time()-begin>timeout:
            raise Exception("Connection timeout", "Timeout waiting for data back from the server (received some data)")
#            break
        #if you got no data at all, wait a little longer
        elif time.time()-begin>timeout*2:
            raise Exception("Connection timeout", "Timeout waiting for data back from the server")
#            break
        try:
            data=the_socket.recv(8192)
            if data:
                total_data.append(data)
                begin=time.time()
            else:
                time.sleep(0.1)
        except Exception as e:
            pass
    return ''.join(total_data)

if __name__ == "__main__":
    
    goback = True
    while(goback):
        genome_file = raw_input("genome file name:")
        print "Use {0}?".format(genome_file)
        cont = raw_input("(Y/N)")
        if (cont.lower()=='y'):
            goback=False
        else:
            genome_file = ''

    with open(genome_file, 'r') as file_handle:
        genome_data = file_handle.read()

    send_job(genome_data, 'gbk', 'custom geneome', 'lairdm@sfu.ca')
