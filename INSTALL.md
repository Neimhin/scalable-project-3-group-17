### cryptography
When running on a raspberry pi the python `cryptography` library won't install
unless you have the rust compiler installed.

Follow the instructions on the rustup website to [install rust](https://rustup.rs/).

Source your .bashrc to make sure `rustc` is on your path:
`source ~/.bashrc`

### install the python dependencies
`pip install -f requirements.txt`
