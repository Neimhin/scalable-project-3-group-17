count=$1
if [ -z "$count" ]; then
	count=3
fi
time python exp/3-node-chain/emulation.py --num-nodes $count
