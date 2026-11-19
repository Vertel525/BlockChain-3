
# Bitcoin duomenų analizė – BlockChain-3

**GitHub:** https://github.com/Vertel525/BlockChain-3

## 1. Projekto aprašymas

Šio projekto tikslas – praktiškai susipažinti su tikros Bitcoin blokų grandinės duomenų struktūra, jų gavimu, dekodavimu, analize ir tikrinimu.

Projekto metu įgyvendintos šios užduotys:

- Bitcoin Merkle Root atkūrimas iš transakcijų identifikatorių.
- Mokomosios maišos funkcijos ir Bitcoin SHA256d palyginimas.
- Vietinio Bitcoin Core mazgo paleidimas naudojant Regtest tinklą.
- Bitcoin transakcijos sukūrimas ir patvirtinimas.
- Blokų grandinės informacijos gavimas per Bitcoin Core RPC.
- Transakcijų mokesčių, SegWit duomenų ir blokų antraščių analizė naudojant Python.

Projektas skirtas mokymosi tikslams. Naudojant Regtest tinklą, atliekami bandymai su vietiniu Bitcoin mazgu, nenaudojant tikrų BTC.

## 2. Naudotos technologijos ir aplinka

Projektas buvo kuriamas ir testuojamas šioje aplinkoje:

| Komponentas | Versija |
|---|---|
| Operacinė sistema | Ubuntu 22.04 LTS (WSL2) |
| Python | 3.10.12 |
| GCC | 11.4.0 |
| CMake | 3.22.1 |
| Libbitcoin System | 3.8.0 |
| Bitcoin Core | 32.1 |
| Git | Naudotas versijų kontrolei |

### Libbitcoin priklausomybės

Libbitcoin System buvo kompiliuojama iš pradinio kodo.

- Libbitcoin System commit: `b60f86ff4ea5ee2c83b2b2cabb4aeed86bb4e69d`
- Libbitcoin secp256k1 commit: `16710e06eaa9f6a0e2cbd7a2585212affc8935f4`

Reikalingų Ubuntu paketų diegimas:

```bash
sudo apt update
sudo apt install build-essential cmake git pkg-config autoconf automake libtool libboost-all-dev libssl-dev libgmp-dev libsqlite3-dev zlib1g-dev
```

Libbitcoin secp256k1 kompiliavimas:

```bash
cd ~/secp256k1
./configure --enable-module-recovery
make clean
make -j$(nproc)
sudo make install
sudo ldconfig
```

Libbitcoin System kompiliavimas:

```bash
cd ~/libbitcoin-system
./configure
make -j$(nproc)
sudo make install
sudo ldconfig
```

## 3. Projekto struktūra

```text
BlockChain-3/
│
├── BitcoinMerkle/
│   ├── CMakeLists.txt
│   ├── main.cpp
│   ├── merkle.cpp
│   ├── merkle.h
│   ├── hash_modes.cpp
│   └── build/
│
├── PythonAnalysis/
│   ├── common.py
│   ├── requirements.txt
│   ├── rpc_example.py
│   ├── rpc_transaction.py
│   ├── rpc_block.py
│   ├── decoded_payment.json
│   ├── legacy_example_raw_hex.txt
│   ├── payment_blockhash.txt
│   ├── payment_txid.txt
│   ├── prevouts.json
│   └── regtest_txids.txt
│
├── Regtest/
│   ├── start_node.ps1
│   ├── stop_node.ps1
│   └── create_wallets_and_payment.ps1
│
├── .gitignore
└── README.md
```

## 4. Bitcoin Merkle Root realizacija

Merkle Root skaičiavimo realizacija yra aplanke `BitcoinMerkle/`.

Skaičiavimams naudojama Libbitcoin System biblioteka, leidžianti atlikti Bitcoin naudojamą dvigubą SHA-256 maišą (SHA256d).

### Algoritmas

1. Transakcijų identifikatoriai (TXID) nuskaitomi tokia tvarka, kokia jie pateikiami bloke. Įtraukiama ir coinbase transakcija.
2. Kiekvienas pateiktas TXID iš šešioliktainio formato konvertuojamas į 32 baitus.
3. Baitų tvarka apverčiama, kad atitiktų vidinį Bitcoin formatą.
4. Du gretimi 32 baitų maišos rezultatai sujungiami į vieną 64 baitų seką.
5. Gautai sekai atliekama dviguba SHA-256 maiša (SHA256d).
6. Jeigu lygyje lieka nelyginis maišų skaičius, paskutinis maišos rezultatas dubliuojamas.
7. Procesas kartojamas tol, kol lieka viena maiša.
8. Galutinis rezultatas konvertuojamas atgal į Bitcoin naudojamą TXID pateikimo baitų tvarką.

Naudojami TXID, o ne WTXID identifikatoriai.

### Istorinio bloko testas

Realizacija patikrinta naudojant Bitcoin Mainnet bloką Nr. 100000.

Tikėtinas Merkle Root:

```text
f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766
```

Apskaičiuota reikšmė sutapo su tikėtinu rezultatu.

### Papildomi testai

Realizacijoje atlikti šie testai:

- Vienos transakcijos.
- Dviejų transakcijų.
- Trijų transakcijų.
- Penkių transakcijų.
- Tuščio TXID sąrašo.
- Neteisingo TXID ilgio.
- Neteisingų šešioliktainių simbolių.
- Pakeisto transakcijos identifikatoriaus.
- Pakeistos transakcijų eiliškumo tvarkos.
- Neteisingos baitų tvarkos.

Testai patvirtino, kad realizacija tinkamai apdoroja nelyginį transakcijų skaičių, atmeta netinkamus duomenis ir pakeitus transakcijų duomenis arba jų eiliškumą gaunamas kitas Merkle Root.

### Regtest Merkle Root testas

Realizacija taip pat patikrinta naudojant vietiniame Regtest tinkle sugeneruotą bloką, kuriame buvo dvi transakcijos:

- Coinbase transakcija.
- 1 BTC mokėjimo transakcija.

Tikėtinas ir apskaičiuotas Merkle Root:

```text
7722452ba66f8ffc501e3f92e72e5dcb9071c3f23f256c4928d69a21676d0ba2
```

Rezultatas sutapo su Bitcoin Core pateikta bloko Merkle Root reikšme.

### Kompiliavimas ir paleidimas

Iš projekto katalogo:

```bash
cd ~/blockchain-3/BitcoinMerkle
cmake -S . -B build
cmake --build build -j$(nproc)
```

Integruotų testų paleidimas:

```bash
./build/bitcoin_merkle
```

Merkle Root skaičiavimas naudojant Regtest transakcijų identifikatorių failą:

```bash
./build/bitcoin_merkle ../PythonAnalysis/regtest_txids.txt
```

## 5. Mokomosios maišos funkcijos ir Bitcoin SHA256d palyginimas

Faile `BitcoinMerkle/hash_modes.cpp` pateikiama atskira dviejų maišos funkcijų demonstracija:

1. Mokomoji maišos funkcija.
2. Bitcoin SHA256d.

Mokomoji maišos funkcija atkuria ankstesniame mokomajame blokų grandinės projekte naudotą algoritmą. Bitcoin SHA256d realizacija naudoja Libbitcoin System biblioteką.

Ši demonstracija yra atskiras šio projekto modulis. Ankstesnio mokomojo projekto failai ir jo versijos nebuvo keičiami.

### Testavimo pavyzdys

Įvestis:

```text
Bitcoin Blockchain
```

Mokomosios maišos rezultatas:

```text
5d860f986724f3b6dbedccb57b5c1a482c6c706da9d625b4e337a889dbb5cf44
```

Bitcoin SHA256d rezultatas:

```text
c050f9ae5e40f20c038e2b6e91287a6bf4c322d3ed41c9c1e74a8a582fde14a4
```

Bitcoin SHA256d rezultatas papildomai patikrintas nepriklausomai naudojant Python `hashlib` biblioteką.

Pakeitus vieną įvesties simbolį gaunamas visiškai kitoks maišos rezultatas. Tai demonstruoja maišos funkcijų jautrumą įvesties pakeitimams.

### Demonstracijos paleidimas

```bash
cd ~/blockchain-3/BitcoinMerkle
./build/hash_modes
```

Pasirenkamas norimas maišos funkcijos režimas ir įvedami duomenys.

## 6. Bitcoin Core Regtest mazgas

Bitcoin Core sukonfigūruotas veikti vietiniame Regtest tinkle.

Regtest leidžia kontroliuojamoje aplinkoje generuoti blokus ir vykdyti transakcijas nenaudojant tikrų Bitcoin.

### Konfigūracija

Mazgas naudoja atskirą duomenų katalogą:

```text
C:\Users\matas\bitcoin-regtest-mif
```

Pateikti trys PowerShell scenarijai:

- `start_node.ps1` – paleidžia Bitcoin Core Regtest mazgą.
- `stop_node.ps1` – sustabdo mazgą.
- `create_wallets_and_payment.ps1` – sukuria pinigines, generuoja blokus ir atlieka mokėjimą.

Scenarijuose naudojami Bitcoin Core vykdomieji failai, esantys:

```text
C:\Program Files\Bitcoin\daemon
```

Scenarijai paleidžiami PowerShell terminale iš projekto katalogo:

```powershell
.\Regtest\start_node.ps1
```

```powershell
.\Regtest\create_wallets_and_payment.ps1
```

```powershell
.\Regtest\stop_node.ps1
```

Naudojant kitą kompiuterį gali reikėti pakeisti Bitcoin Core vykdomojo failo ir duomenų katalogo kelius.

### Piniginių sukūrimas ir blokų generavimas

Sukurtos dvi piniginės:

- `MIF` – naudojama blokams generuoti ir mokėjimui siųsti.
- `student` – naudojama mokėjimui gauti.

Pradžioje sugeneruoti 101 blokas.

Po generavimo MIF piniginėje buvo:

- 50 BTC patvirtintas (trusted) likutis.
- 5000 BTC nebrandus (immature) likutis.

Nebrandus likutis reiškia, kad kasimo atlygis dar nepasiekė reikalaujamo brandumo.

### Mokėjimo sukūrimas

Iš MIF piniginės į student piniginę išsiųstas 1 BTC mokėjimas.

Naudotas 2 sat/vB transakcijos mokesčio tarifas.

Iš pradžių transakcija patikrinta mempool eilėje, o vėliau patvirtinta sugeneravus dar vieną bloką.

Gautas bloko aukštis – 102.

### Transakcijos ir bloko identifikatoriai

Transakcijos ID:

```text
e99241b47c51d5bb2dd496972b6b7d2787d2ee37b05ad91fc033fdb76f4a4239
```

Bloko hash:

```text
3ffd7eef8f9a8552b217f6be997ba74ce208acfb7f2add29fafb710b8eeb888d
```

Bloke buvo dvi transakcijos, o analizuojant mokėjimas turėjo vieną patvirtinimą.

## 7. Bitcoin blokų grandinės analizė naudojant Python

Python programos yra aplanke `PythonAnalysis/`.

Jos naudoja standartines Python bibliotekas ir Bitcoin Core CLI komandas. Papildomų pip paketų nereikia.

`requirements.txt` failas paliktas tuščias, nes papildomos Python priklausomybės nenaudojamos.

### common.py

Faile pateikiamos bendros funkcijos:

- Bitcoin Core CLI komandų vykdymui.
- JSON atsakymų gavimui ir dekodavimui.
- BTC konvertavimui į satoshi.
- Satoshi konvertavimui į BTC.
- Ankstesnių transakcijų išvesčių (prevouts) įkėlimui.

Dabartinė konfigūracija naudoja Windows Bitcoin Core diegimą per WSL. Naudojant kitą aplinką, `common.py` faile reikia pakeisti vykdomojo failo ir duomenų katalogo kelius.

### rpc_example.py

Programa gauna aktualią informaciją iš Bitcoin Core.

Pateikiama:

- Aktyvus blokų grandinės tinklas.
- Blokų ir antraščių skaičius.
- Pradinio sinchronizavimo būsena.
- Bitcoin Core versija.
- Tinklo ryšių skaičius.
- Dabartinis stebėjimo laikas.

Testuojant vietinį mazgą buvo gautas nulinis tinklo ryšių skaičius. Izoliuotame vietiniame Regtest mazge tai yra normalu.

### rpc_transaction.py

Programa analizuoja sukurtą 1 BTC mokėjimo transakciją.

Gaunami ir analizuojami:

- Transakcijos ID ir WTXID.
- Įvesties ir išvesties reikšmės.
- Transakcijos mokestis.
- Mokesčio tarifas.
- Išvesčių adresai ir skriptų tipai.
- SegWit liudytojo (witness) informacija.
- Transakcijos dydis, virtualus dydis ir svoris.

Gauti testavimo rezultatai:

| Savybė | Reikšmė |
|---|---:|
| Įvesties vertė | 50 BTC |
| Išvesties vertė | 49.99999718 BTC |
| Mokestis | 0.00000282 BTC |
| Mokestis satoshi | 282 sat |
| Mokesčio tarifas | 2 sat/vB |
| Transakcijos dydis | 222 baitai |
| Bazinis dydis | 113 baitų |
| Virtualus dydis | 141 vB |
| Svoris | 561 WU |

Mokestis apskaičiuojamas pagal formulę:

```text
Mokestis = Visų įvesčių vertė - Visų išvesčių vertė
```

Apskaičiuotas mokestis taip pat palygintas su piniginės pateiktu mokesčiu. Reikšmės sutapo.

### SegWit analizė

Mokėjime naudojamos native SegWit išvestys.

Įvesties `scriptSig` yra tuščias, o liudytojo (witness) duomenyse saugomi parašas ir viešasis raktas.

Patikrinti šie ryšiai:

```text
Svoris = 3 * Bazinis dydis + Bendras dydis
```

```text
Virtualus dydis = ceil(Svoris / 4)
```

Abu skaičiavimai sutapo su Bitcoin Core pateiktais transakcijos duomenimis.

### Legacy transakcijos palyginimas

Palyginimui naudota legacy coinbase transakcija iš Bitcoin Genesis bloko.

Jos TXID ir WTXID sutampa, nes transakcijoje nėra SegWit liudytojo duomenų.

Transakcija neturi witness duomenų, o bazinis dydis sutampa su bendru dydžiu.

### rpc_block.py

Programa analizuoja Bitcoin bloką naudodama Bitcoin Core RPC sąsają.

Pateikiama:

- Bloko hash.
- Bloko aukštis.
- Transakcijų skaičius.
- Visų transakcijų išvesčių suma.
- Atkurta 80 baitų bloko antraštė.
- Palyginimas su Bitcoin Core pateikta neapdorota antrašte.
- Nepriklausomai apskaičiuotas bloko hash.
- Hash palyginimas pakeitus nonce reikšmę.

Patikrinta, kad atkurta antraštė sutampa su Bitcoin Core pateikta neapdorota antrašte, o apskaičiuotas hash sutampa su bloko hash.

Programa taip pat išsaugo bloko transakcijų identifikatorius faile `regtest_txids.txt`.

Testuoto bloko visų išvesčių suma:

```text
100 BTC
```

Ši suma apima coinbase transakciją ir grąžą. Todėl jos negalima laikyti tikrąja ekonominių mokėjimų apimtimi.

### Python programų paleidimas

Programas reikia paleisti iš `PythonAnalysis` katalogo:

```bash
cd ~/blockchain-3/PythonAnalysis
python3 rpc_example.py
```

```bash
python3 rpc_transaction.py
```

Naujausio bloko analizė:

```bash
python3 rpc_block.py
```

Konkretaus bloko analizė:

```bash
python3 rpc_block.py 3ffd7eef8f9a8552b217f6be997ba74ce208acfb7f2add29fafb710b8eeb888d
```

Prieš paleidžiant Python programas turi veikti Bitcoin Core Regtest mazgas.

## 8. Rezultatai ir išvados

Projekto metu praktiškai patikrinti keli svarbūs Bitcoin veikimo principai.

- Bitcoin Merkle Root galima atkurti iš transakcijų identifikatorių, naudojant teisingą baitų tvarką ir SHA256d.
- Esant nelyginiam Merkle medžio maišų skaičiui, paskutinė maiša dubliuojama.
- Bitcoin SHA256d rezultatai skiriasi nuo mokomosios maišos funkcijos rezultatų.
- Vietinis Bitcoin Core Regtest mazgas gali generuoti blokus ir vykdyti transakcijas nenaudodamas tikrų lėšų.
- Transakcijos mokestį galima nepriklausomai apskaičiuoti naudojant ankstesnes išvestis ir naujas išvestis.
- SegWit transakcijose TXID ir WTXID gali skirtis, o papildomi duomenys saugomi witness dalyje.
- Bitcoin bloko antraštę galima atkurti iš atskirų laukų ir nepriklausomai apskaičiuoti jos hash.
- Visų bloko transakcijų išvesčių suma nebūtinai atitinka ekonominių mokėjimų apimtį.

Visi realizuoti Merkle testai ir aprašyti Regtest transakcijos bei bloko tikrinimo bandymai buvo sėkmingi.

## 9. Projekto saugykla

GitHub:

https://github.com/Vertel525/BlockChain-3
