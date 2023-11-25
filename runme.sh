# remove logs from previous run
rm -r logs
# make logs folder
mkdir -p logs

# start the master emulator
printf "starting master emulator..."
python ./src/master_emulator.py \
	1> logs/master_emulator.stdout \
	2> logs/master_emulator.stderr &
sleep 1
printf "done\n"

# start three slave emulators
for l in 1 2 3; do
  printf "starting slave $l..."
  python ./src/slave_emulator.py --num-nodes 45 \
	  1> logs/slave_emulator_$l.stdout \
	  2> logs/slave_emulator_$l.stderr &
  sleep 3
  printf "done\n"
done

# open the web gui in your browser
open http://localhost:33000
