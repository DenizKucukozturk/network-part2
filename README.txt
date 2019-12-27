2166023 İLKER BULAK
2171759 MUSTAFA DENİZ KÜÇÜKÖZTÜRK
Group 1

1) Both of the experiments can be called with "sudo client.py <experiment no>" and "sudo server.py <experiment no>"
 on server and client sides. For example "sudo client.py 1" for experiment 1. Internal nodes (r1,r2,r3) can be called
 with their relative named script files "sudo r1.py","sudo r2.py","sudo r3.py". R1, r2 and r3 scripts only redirects
 incoming packets to "s" or "d".

2)Call client.py at node s. Call server.py at node d

2) Both client and server scripts includes print functions for ease of use. Server function also prints start time,
end time and difference between them. Start time is the time of the first sent packet. End time is the time of last
acknowledment. Difference is the difference between them which means total time spent for sending file. As end time
and receive time are calculated at the same node there is no need for time syncronization .

3)Server file saves received file into "input.txt". If there exists such a file before , than it will
append downloaded file toward it. Thus it will give wrong result. Delete input.txt file before calling
server.py.

4)For Link delay(+loss) scripts are included according to their relative names (for example "r1-delay.sh").
If another delay added before change the "add" keyword to "change". For Example:
sudo tc qdisc add dev $s_adapter root netem loss 38% delay 3ms
sudo tc qdisc change dev $s_adapter root netem loss 38% delay 3ms

5) We used the same topology as in part1 of the project. Thus IP values are same as in part1.

6) Port values for receiving sides in communications:
  S to R1: 10
  S to R2: 50
  S to R3: 40
  D to R1: 30
  D to R2: 70
  D to R3: 60
  R1 to S: 40
  R1 to D: 20
  R2 to S: 80
  R2 to D: 60
  R3 to S: 70
  R3 to D: 50

7) Execution Ordering:

  For experiment 1:
    --Run the delay scripts for all nodes. First experiment for %5 than %15 and lastly for %38.
     (For loss %5 change nothing, For loss %15 change "add" keyword to "change" and
        change "5%" part of it to "15%", For loss %38 change "15%" part of it to "38%" ).

    --Call python codes as described in 1.note .Running order should be s,r3,d.
    --You can see passed time in terminal
  For experiment 2:
  --Run the delay scripts for all nodes. First experiment for %5 than %15 and lastly for %38.
     (For loss %5 change nothing, For loss %15 change "add" keyword to "change" and
      change "5%" part of it to "15%", For loss %38 change "15%" part of it to "38%" ).
  --Call python codes as described in 1.note .Running order should be s,r1,r2,d.
  --Program can handle 1 link down. Link down may be on r1 or r2.
  --To down a link you can use ctrl z in r1 or r2. (Or ip link set dev <interface> down)
  --You can see passed time in terminal
