s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

sudo tc qdisc add dev $s_adapter root netem loss 5% delay 3ms

sudo tc qdisc add dev $d_adapter root netem loss 5% delay 3ms
