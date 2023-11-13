if [ -z "$1" ]; then
	pi=pi
else
	pi=$1
fi
ssh -L 5000:localhost:5000 $pi
