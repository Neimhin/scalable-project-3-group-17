### cryptography
When running on a raspberry pi the python `cryptography` library won't install
unless you have the rust compiler installed.

Follow the instructions on the rustup website to [install rust](https://rustup.rs/).

Source your .bashrc to make sure `rustc` is on your path:
`source ~/.bashrc`

With rustc installed on the pi you should now be able to install the pip `cryptography` library:
`pip install cryptography`.

### install the rest of the python dependencies
`pip install -r requirements.txt`
