
emulator_port=$1
if [ -z "$emulator_port" ]; then
	emulator_port=34000
fi
url="http://localhost:$emulator_port/all_dbs"
echo "$url"
curl -X GET "$url"
