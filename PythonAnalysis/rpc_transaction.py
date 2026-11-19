import argparse
from decimal import Decimal
from common import bitcoin_json, bitcoin_cli, load_prevouts, satoshi_to_btc


def main():
    parser = argparse.ArgumentParser(description="Regtest transakcijos analizė")
    parser.add_argument("txid", help="Savo 1 BTC mokėjimo TXID")
    parser.add_argument("blockhash", nargs="?", help="Mokėjimą patvirtinusio bloko hash")
    parser.add_argument("--prevouts", default="prevouts.json", help="Prieš mokėjimą išsaugotas listunspent JSON")
    args = parser.parse_args()

    wallet_tx = bitcoin_json("gettransaction", args.txid, wallet="MIF")
    blockhash = args.blockhash or wallet_tx.get("blockhash")
    if not blockhash:
        raise RuntimeError("Transakcija dar neturi blockhash. Pirmiausia patvirtink ją bloke.")

    tx = bitcoin_json("getrawtransaction", args.txid, "true", blockhash)
    prevouts = load_prevouts(args.prevouts)

    input_total = 0
    print("Transakcijos įvestys:")
    for index, vin in enumerate(tx.get("vin", [])):
        if "coinbase" in vin:
            print(f"  Įvestis {index}: coinbase (įprastas mokestis neskaičiuojamas)")
            continue

        key = (vin["txid"], int(vin["vout"]))
        amount = prevouts.get(key)
        source = "prevouts.json"
        if amount is None:
            previous_tx = bitcoin_json("getrawtransaction", vin["txid"], "true")
            amount = int(Decimal(str(previous_tx["vout"][int(vin["vout"])]["value"])) * Decimal("100000000"))
            source = "ankstesnė transakcija per RPC"

        input_total += amount
        print(f"  {index}: txid={vin['txid']} vout={vin['vout']} suma={satoshi_to_btc(amount)} BTC ({source})")

    output_total = 0
    print("\nTransakcijos išvestys:")
    for index, vout in enumerate(tx.get("vout", [])):
        amount = int(Decimal(str(vout["value"])) * Decimal("100000000"))
        output_total += amount
        script = vout.get("scriptPubKey", {})
        print(f"  {index}: {satoshi_to_btc(amount)} BTC, tipas={script.get('type', 'nenurodytas')}, adresai={script.get('address', script.get('addresses', []))}")

    if tx.get("vin") and "coinbase" not in tx["vin"][0]:
        fee = input_total - output_total
        print("\nĮvesčių suma:", satoshi_to_btc(input_total), "BTC")
        print("Išvesčių suma:", satoshi_to_btc(output_total), "BTC")
        print("Apskaičiuotas mokestis:", satoshi_to_btc(fee), "BTC")
        wallet_fee = abs(int(Decimal(str(wallet_tx.get("fee", 0))) * Decimal("100000000")))
        print("Piniginės gettransaction fee absoliuti vertė:", satoshi_to_btc(wallet_fee), "BTC")
        print("Mokesčio sutapimas:", "TAIP" if fee == wallet_fee else "NE – patikrink prevouts duomenis")
        if tx.get("vsize"):
            print("Faktinis tarifas:", Decimal(fee) / Decimal(tx["vsize"]), "sat/vB")

    print("\nIdentifikatoriai ir dydžiai:")
    print("txid:", tx.get("txid"))
    print("wtxid (RPC hash):", tx.get("hash"))
    print("size:", tx.get("size"))
    print("vsize:", tx.get("vsize"))
    print("weight:", tx.get("weight"))
    if tx.get("weight") is not None and tx.get("size") is not None:
        base_size = (int(tx["weight"]) - int(tx["size"])) // 3
        print("base_size:", base_size)
        print("Patikra weight = 3 * base_size + total_size:", 3 * base_size + int(tx["size"]) == int(tx["weight"]))
        print("Patikra vsize = ceil(weight / 4):", (int(tx["weight"]) + 3) // 4 == int(tx["vsize"]))

    print("\nĮvesčių scriptSig ir witness:")
    for index, vin in enumerate(tx.get("vin", [])):
        print(f"  Įvestis {index} scriptSig:", vin.get("scriptSig", {}).get("hex", ""))
        print(f"  Įvestis {index} txinwitness:", vin.get("txinwitness", []))

    print("\nPaaiškinimas: txid apskaičiuojamas iš transakcijos be witness duomenų, o wtxid – su witness duomenimis.")
    print("Witness duomenys keičia svorį ir wtxid, bet ne txid.")

    legacy_file = "legacy_example_raw_hex.txt"
    try:
        with open(legacy_file, "r", encoding="utf-8-sig") as file:
            legacy_hex = file.read().strip()
        legacy = bitcoin_json("decoderawtransaction", legacy_hex)
        print("\nLegacy palyginimas (išsaugota genesis coinbase raw transakcija):")
        print("txid:", legacy.get("txid"))
        print("wtxid/hash:", legacy.get("hash"))
        print("size:", legacy.get("size"), "vsize:", legacy.get("vsize"), "weight:", legacy.get("weight"))
        print("Legacy turi witness:", any(vin.get("txinwitness") for vin in legacy.get("vin", [])))
        print("Legacy atveju base_size = total_size:", legacy.get("size") == legacy.get("vsize"))
        print("Legacy patikra weight = 4 * size:", int(legacy["weight"]) == 4 * int(legacy["size"]))
        for index, vin in enumerate(legacy.get("vin", [])):
            print(f"  Legacy įvestis {index} scriptSig:", vin.get("scriptSig", {}).get("hex", ""))
            print(f"  Legacy įvestis {index} txinwitness:", vin.get("txinwitness", []))
        print("Palyginimas: regtest mokėjimo witness tikrinamas aukščiau pagal kiekvieną vin.")
    except FileNotFoundError:
        print("Legacy raw failas nerastas – palyginimas praleistas.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, ValueError, OSError) as error:
        print("Klaida:", error)
