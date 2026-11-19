from datetime import datetime, timezone
from common import bitcoin_json, bitcoin_cli


def main():
    info = bitcoin_json("getblockchaininfo")
    network = bitcoin_json("getnetworkinfo")

    print("Bitcoin Core RPC informacija")
    print("Stebėjimo laikas (UTC):", datetime.now(timezone.utc).isoformat())
    print("Chain:", info["chain"])
    print("Blocks:", info["blocks"])
    print("Headers:", info["headers"])
    print("Initial block download:", info["initialblockdownload"])
    print("Bitcoin Core versija:", network["version"])
    print("Ryšių skaičius:", network["connections"])
    print("Mazgo būsena gauta per gyvą RPC užklausą.")

    if info["chain"] != "regtest":
        print("ĮSPĖJIMAS: naudojamas ne regtest tinklas.")
    if network["connections"] == 0:
        print("0 ryšių izoliuotame vietiniame regtest mazge yra normalu.")
    if info["blocks"] == 0:
        print("0 blokų reiškia, kad šiame laboratorijos kataloge dar negeneruota blokų.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, ValueError) as error:
        print("Klaida:", error)
