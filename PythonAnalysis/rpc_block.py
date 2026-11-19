import argparse
import hashlib
import struct
from decimal import Decimal
from common import bitcoin_json, bitcoin_cli


def create_header(block):
    version = struct.pack("<I", int(block["version"]) & 0xffffffff)
    previous_hash = bytes.fromhex(block["previousblockhash"])[::-1]
    merkle_root = bytes.fromhex(block["merkleroot"])[::-1]
    block_time = struct.pack("<I", int(block["time"]))
    bits = struct.pack("<I", int(block["bits"], 16))
    nonce = struct.pack("<I", int(block["nonce"]))
    header = version + previous_hash + merkle_root + block_time + bits + nonce
    if len(header) != 80:
        raise ValueError("Bloko antraštė turi būti 80 baitų.")
    return header


def sha256d(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def main():
    parser = argparse.ArgumentParser(description="Regtest bloko analizė")
    parser.add_argument("blockhash", nargs="?", help="Bloko hash; jei nenurodytas, naudojamas geriausias blokas")
    args = parser.parse_args()

    blockhash = args.blockhash or bitcoin_cli("getbestblockhash")
    block = bitcoin_json("getblock", blockhash, 2)

    total_outputs = Decimal("0")
    transaction_count = len(block["tx"])
    for tx in block["tx"]:
        for output in tx.get("vout", []):
            total_outputs += Decimal(str(output["value"]))

    print("Bloko suvestinė")
    print("Hash:", block["hash"])
    print("Aukštis:", block["height"])
    print("Transakcijų skaičius:", transaction_count)
    print("Visų transakcijų išvesčių suma:", total_outputs, "BTC")
    print("Pastaba: suma apima coinbase ir grąžą, todėl nėra ekonominių mokėjimų apimtis.")

    header = create_header(block)
    raw_header = bitcoin_cli("getblockheader", blockhash, "false")
    print("\nBloko antraštė")
    print("Sukurta antraštė (80 baitų):", header.hex())
    print("RPC raw antraštė:", raw_header)
    print("Baitų sutapimas:", header.hex() == raw_header.lower())

    calculated_hash = sha256d(header)[::-1].hex()
    print("Apskaičiuotas block hash:", calculated_hash)
    print("RPC block hash:", blockhash)
    print("Maišos sutapimas:", calculated_hash == blockhash)

    changed_header = create_header({**block, "nonce": (int(block["nonce"]) + 1) & 0xffffffff})
    changed_hash = sha256d(changed_header)[::-1].hex()
    print("Hash pakeitus nonce:", changed_hash)
    print("Nonce pakeitė hash:", changed_hash != calculated_hash)

    with open("regtest_txids.txt", "w", encoding="utf-8") as file:
        for tx in block["tx"]:
            file.write(tx["txid"] + "\n")
    print("\nBloko TXID sąrašas išsaugotas faile regtest_txids.txt")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, ValueError, OSError) as error:
        print("Klaida:", error)
