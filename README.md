## TurboTap Eclipse

##### RPC clicker.

##### Features:
- Clicking

## Install

Install [python 3.12](https://www.python.org/downloads/release/python-3120/)


Linux:
```shell
python3.12 -m venv venv && \
. ./venv/bin/activate && \
pip install -r requirements.txt
```

Windows
```powershell
python -m venv venv
. .\venv\Scripts\activate
pip install -r .\requirements.txt
```

## Configuration

Provide delay in `config.toml` with start delay `delay_from` and end delay `delay_to`

```toml
# config.toml

delay_from = 5
delay_to = 20
```


#### Proxies
Provide proxies in `proxies.txt` in format `http://username:password@ip:port`.

#### Wallets
Provide wallet private keys in `wallets.txt` in format `list[int]`

**How to get required private keys?**

1. Go to https://tap.eclipse.xyz/ and sign in.
2. F12 -> Console.
3. Type:
```javascript
localStorage.getItem("wallet")
```
4. Right click on response -> "Copy string contents".
5. Paste into `wallets.txt`

![step](./assets/step.png)


## Run

Linux:
```shell
python3.12 src/main.py
```

Windows:
```powershell
python .\src\main.py
```
