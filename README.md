# cdpnotify
MakerDAO CDP Collateralization Notification Bot for Telegram.

### Commands
```
/watch <cdp_id> [<ratio>]: Add a CDP with the given ID to your watchlist.
The bot will send you a private notification if the collateralization is below the given ratio (default=200%)

/unwatch <cdp_id>: Remove CDP from your watchlist

/status: Show your current watchlist

/help: Show this message
```

### Using the already deployed instance
A instance of this bot is already deployed under [@cdpnotifybot](https://t.me/CDPNotifyBot).
NOTE: This instance is hosted by me and it will save your Telegram Id associated with the CDP Ids you are watching (this data will be deleted once you issue `/unwatch`).
Also I cannot guarantee a 24/7 uptime, so dont rely solely on this bot!


### Installation
The following steps are made for Linux/MacOS environment

**1. Clone repo**
```bash
git clone https://github.com/gcarq/cdpnotify.git
cd cdpnotify
```

**2. Create config file**  
```bash
cp config.json.example config.json
vi config.json
```

**3. Install dependencies**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Docker
```bash
touch cdps.sqlite
docker build -t cdpnotify .
docker run --rm \
    -v /etc/localtime:/etc/localtime:ro \
    -v `pwd`/config.json:/cdpnotify/config.json \
    -v `pwd`/cdps.sqlite:/cdpnotify/cdps.sqlite \
    -it cdpnotify
```

### Software requirements
- [Python 3.6.x](http://docs.python-guide.org/en/latest/starting/installation/) 
- [pip](https://pip.pypa.io/en/stable/installing/)
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) (Recommended)
- [Docker](https://www.docker.com/products/docker) (Recommended)


##### Please consider making a small donation if you find this bot useful:

`ETH: 0x7f07523856BEf9c0a6153A703dE613D6F19e82e4`