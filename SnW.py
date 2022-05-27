
#run using:
#python3 SnW.py


from random import random

class Message:
    def __init__(self,p,n,data=None):
        self.corrupted=False
        self.prob_failure=p
        self.n=n
        self.data=data

##        if self.data:
##            print(f"DATA FRAME: n={n}, data={data}")
##        else:
##            print(f"ACK: n={n}")
        
    def corrupt(self):
        if random()<self.prob_failure:
            self.corrupted=True
            #print("corrupted")

#sender class
class Sender:
    def __init__(self,data,prob_send_fail):
        #data index
        self.data=data
        self.data_index=0

        #error probability
        self.prob_send_fail=prob_send_fail

        #parity bit for error detection
        self.expected_n=0

        #for the fake timer
        self.timer=True #start off as True: that way, the first frame will be sent

    def done(self):
        """ return whether the sender is done sending """
        return self.data_index==len(self.data)

    def start_timer(self):
        self.timer=True
    def stop_timer(self):
        self.timer=False
    def check_timer(self):
        """ return whether the timer is on and has reached the threshold """
        return self.timer


    def handle(self,msg=None):
        """ handle incoming ACK """
        if msg and not msg.corrupted and msg.n==self.expected_n:
            #succesful acknowledgement

            self.stop_timer()

            #go to next frame, flip parity bit
            self.data_index+=1
            self.expected_n=1-self.expected_n #could also be self.data_index%2

            #if not done, send next frame
            if not self.done():
                self.start_timer()
                return self.create_frame(self.expected_n)

        
        elif self.check_timer() and not self.done(): #at this point check_timer is always true - we use a fake timer
            return self.create_frame(self.expected_n)
        
        return None
    
    def create_frame(self,n):
        return Message(self.prob_send_fail,n,self.data[self.data_index])

class Receiver:
    def __init__(self,prob_ack_fail):
        #received data
        self.received=[]

        #error probability
        self.prob_ack_fail=prob_ack_fail

        #parity bit for error detection
        self.expected_n=0

    
    def handle(self,frame):
        """
        handle incoming frame
        
        returns:
            ACK message if applicable
            else None

        """
        #print(frame)
        
        if frame and not frame.corrupted: #frame arrived uncorrupted
            if frame.n==self.expected_n: #new data; register and update
                self.received.append(frame.data)
                self.expected_n=1-self.expected_n
                
            return self.create_ack(frame.n) #send back ACK
        return None
            
    def create_ack(self,n):
        """ create ACK back to sender """
        return Message(self.prob_ack_fail,n)


def send(data,prob_send_fail,prob_ack_fail):
    """ send data and return iterations needed """
    sender=Sender(data,prob_send_fail)
    receiver=Receiver(prob_ack_fail)

    count=0 #count iterations
    frame = sender.handle(None) #start by sending first frame
    while not sender.done():

        #potentially corrupt frame
        if frame:
            frame.corrupt()

        #frame is received; get ack back
        ack=receiver.handle(frame)

        #potentially corrupt ack
        if ack:
            ack.corrupt()

        #receive ack; create new frame if applicable
        frame=sender.handle(ack)
        

        count+=1

    #check that received data matches sent data
    assert DATA==receiver.received

    return count





if __name__=="__main__":

    #load data from file
##    with open("input","r") as f:
##        data=f.read()
##
##    data=list(map(int,data.split()))
    
    #generate some data
##    DATA=list("Hello World!")

    #helper function
    def frange(start=0,stop=None,step=1):
        """ float range function """
        if stop==None:
            stop=start
            start=0
        return (start+i*step for i in range(int((stop-start)/step)))


    ### Experiment 1
    print("EX 1")
    
    ex1_data={}

    #no errors
    PROB_ACK_FAIL=0
    PROB_SEND_FAIL=0
    
    #test for various lengths
    for S in range(0,200+20,20):
        DATA=list(range(S))
        
        ex1_data[S]=send(DATA,PROB_SEND_FAIL,PROB_ACK_FAIL)

    print("Ex 1 done")

    ### Experiment 2
    print("EX 2")
    
    ex2_data={}

    #no errors in ACK
    PROB_ACK_FAIL=0

    #200 numbers
    S=200
    DATA=list(range(S))

    #average over N readings
    N2=500#000

    #vary frame error probability
    for PROB_SEND_FAIL in frange(0,1,0.05):
        print("%.2f"%PROB_SEND_FAIL)
        #take average of 1000 runs
        counts=[send(DATA,PROB_SEND_FAIL,PROB_ACK_FAIL) for i in range(N2)]
        count=sum(counts)/len(counts)
        ex2_data[PROB_SEND_FAIL]=count

    print("Ex 2 done")

    ### Experiment 3
    print("EX 3")
    
    ex3_data={}

    #100 numbers
    S=100
    DATA=list(range(S))

    #average over N readings
    N3=100#0

    #vary frame error probability
    for P in frange(0,1,0.05):
        print("%.2f"%P)
        #take average of 1000 runs
        counts=[send(DATA,P,P) for i in range(N3)]
        count=sum(counts)/len(counts)
        ex3_data[P]=count

    print("Ex 3 done")

    #print(f"Message length: {len(DATA)}\nIterations: {count}")

    import matplotlib.pyplot as plt

    plt.plot(*list(zip(*ex1_data.items())),'-o')
    plt.xlabel("Message length")
    plt.ylabel("Iterations")
    plt.savefig('ex1.png')
    plt.show()
    plt.plot(*list(zip(*ex2_data.items())),'-o')
    plt.xlabel("P1")
    plt.ylabel(f"Iterations (average of {N2})")
    plt.savefig('ex2.png')
    plt.show()
    plt.plot(*list(zip(*ex3_data.items())),'-o')
    plt.xlabel("P")
    plt.ylabel(f"Iterations (average of {N3})")
    plt.savefig('ex3.png')
    plt.show()







    
