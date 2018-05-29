# cdpnotify

MakerDAO CDP Collateralization Notification Bot for Telegram.

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