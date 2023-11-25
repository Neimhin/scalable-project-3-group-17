### Requirements
The python library dependencies are listed in `requirements.txt`, but if running on raspberry pis
you will need to follow the instructions in `INSTALL.md`.

### Running the Emulators
We have provided the `runme.sh` which has been testing on debian linux.

As an explanation the script first starts a master emulator with `python ./src/master_emulator.py`.

It then starts three slave emulators, with each slave emulator emulating 45 devices:
`python ./src/slave_emulator.py`.

The slave emulators have to be started after the master emulator and should not be started at the same time so that they can
each find free ports for all their devices.


Finally the script runs `open localhost:33000`, which on debian linux opens the webbrowser to the web GUI for the emulation.
If you don't have the `open` command or it is configured differently then just navigate to `localhost:33000` in your browser.

The Web GUI requires an internet connection to download some javascript libraries from CDNs.

### Navigating the Web GUI
First try refreshing the topology (press the button that says 'refresh topology'), to see an visualization of the network topology.

Then run a test by clicking the `start singe datum test 1` buttons.
This will identify two nodes in the network where the shortest path between them is 1 hop. It will put data in the cache of one, and trigger a `desire` for that data in the other.
Give it a couple of seconds and then click the `refresh test report` button to see a report of the test, namely which devices were in the test, whethere it passed, the data in the caches of the relevant devices.

### Debugging the State of the Emulators
Each slave emulator will respond to some debug requests to check, e.g. the cache, the PIT, the desire history, the request history.
There are example scripts in the `./debug/` folder to query the state of the devices in the first emulator. These scripts take an optional parameter of the port of the slave emulator to query. The first emulator will take the port 34000, the next will take 33999, etc.
