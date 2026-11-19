import json
import subprocess
from decimal import Decimal
from pathlib import Path

DEFAULT_DATADIR = Path(r"C:\Users\matas\bitcoin-regtest-mif")


def bitcoin_cli(*args, wallet=None, datadir=None):
    data_dir = Path(datadir) if datadir else DEFAULT_DATADIR
    command = ["/mnt/c/Program Files/Bitcoin/daemon/bitcoin-cli.exe", "-regtest", f"-datadir={data_dir}"]
    if wallet:
        command.append(f"-rpcwallet={wallet}")
    command.extend(str(arg) for arg in args)

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Nerastas bitcoin-cli. Pridėk Bitcoin Core katalogą prie PATH "
            "arba paleisk programą terminale, kuriame bitcoin-cli pasiekiamas."
        )
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or error.stdout.strip()
        raise RuntimeError(f"Bitcoin Core RPC klaida: {message}")

    return result.stdout.strip()


def bitcoin_json(*args, wallet=None, datadir=None):
    raw = bitcoin_cli(*args, wallet=wallet, datadir=datadir)
    return json.loads(raw, parse_float=Decimal, parse_int=int)


def btc_to_satoshi(value):
    return int(Decimal(str(value)) * Decimal("100000000"))


def satoshi_to_btc(value):
    return Decimal(value) / Decimal("100000000")


def load_prevouts(path="prevouts.json"):
    file_path = Path(path)
    if not file_path.exists():
        return {}

    with file_path.open("r", encoding="utf-8-sig") as file:
        items = json.load(file, parse_float=Decimal, parse_int=int)

    result = {}
    for item in items:
        result[(item["txid"], int(item["vout"]))] = btc_to_satoshi(item["amount"])
    return result
