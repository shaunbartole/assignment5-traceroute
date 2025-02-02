import socket
from socket import *
import os
import sys
import struct
import time
import select
import binascii
from socket import socket

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
    #Fill in start
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.

    # Don’t send the packet yet , just return the final packet in this function.

    myChecksum = 0

    myID = os.getpid() & 0xFFFF
    sendTime = time.time()

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
    data = struct.pack("d", sendTime)

    myChecksum = checksum(header + data)
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)

    #Fill in end

    # So the function ending should look like this

    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    tracelist1 = [] #This is your list to use when iterating through each trace 
    tracelist2 = [] #This is your list to contain all traces

    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)

            #Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET,SOCK_RAW,icmp)
            #Fill in end
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    tracelist2.append([str(ttl),tracelist1[-1]])
                    #Fill in end
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    tracelist1.append("* * * Request timed out.")
                    #Fill in start
                    tracelist2.append([str(ttl),tracelist1[-1]])
                    #Fill in end
            except timeout:
                continue

            else:
                #Fill in start
                #Fetch the icmp type from the IP
                icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq, timeSent = struct.unpack('bbHHhd',recvPacket[20:36])
                types, = struct.unpack('b', recvPacket[20:21])
                #Fill in end
                try: #try to fetch the hostname
                    #Fill in start
                    sourceHostname = gethostbyaddr(addr[0])[0]
                    #Fill in end
                except herror:  #if the host does not provide a hostname
                    #Fill in start
                    sourceHostname = "hostname unreturnable"
                    #Fill in end

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 +
                    bytes])[0]
                    #Fill in start
                    rtt = str(round(timeSent*1000)) +"ms"
                    tracelist1.append([str(ttl),rtt,str(addr[0]),sourceHostname])
                    tracelist2.append(tracelist1[-1])
                    #print("   %d     rtt=%.0f ms    %s" % (ttl, (timeReceived - t) * 1000, addr[0]))
                    #Fill in end
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start
                    rtt = "*"
                    tracelist1.append([str(ttl), rtt,str(addr[0]), sourceHostname,"Request timed out"])
                    tracelist2.append(tracelist1[-1])


                    #Fill in end
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #Fill in start

                    #You should add your responses to your lists here and return your list if your destination IP is met
                    #rtt = str(round((t - timeSent)*1000)) +"ms"
                    tracelist1.append(str(ttl))
                    tracelist1.append(str(int((timeReceived - timeSent) * 1000)) + "ms")
                    tracelist1.append(addr[0])
                    tracelist1.append(str(destAddr))
                    tracelist2.append(tracelist1)

                    #tracelist1.append([str(ttl), rtt, destAddr])
                    #tracelist2.append(tracelist1[-1])
                    print(tracelist2)
                    return tracelist2
                    #Fill in end

                    return
                else:
                    #Fill in start
                    #If there is an exception/error to your if statements, you should append that to your list here
                    tracelist1.append([str.ttl,rtt,str(addr[0]),'*','Error Occurred'])
                    #Fill in end
                break
            finally:
                mySocket.close()

if __name__ == '__main__':
    get_route("google.co.il")