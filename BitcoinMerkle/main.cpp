
#include "merkle.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

int main(int argc, char* argv[])
{
    vector<string> historical = {
        "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87",
        "fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4",
        "6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4",
        "e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d"
    };

    const string expected =
        "f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766";

    try
    {
        cout << "Bitcoin Merkle medis (Libbitcoin)" << endl;
        cout << "Istorinis blokas 100000:" << endl;

        const vector<string> expectedRoots = {
            "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87",
            "ccdafb73d8dcd0173d5d5c3c9a0770d0b3953db889dab99ef05b1907518cb815",
            "fa435470825de273081dcc706b25514c936fa6dc80ab965ce6970d68ddd0b553"
        };

        for (int count = 1; count <= 3; count++)
        {
            vector<string> test(
                historical.begin(),
                historical.begin() + count
            );

            string root = calculateBitcoinMerkleRoot(test);

            cout << count << " lapai: " << root
                 << " - "
                 << (root == expectedRoots[count - 1]
                     ? "TEISINGAS" : "KLAIDA")
                 << endl;
        }

        string historicalRoot = calculateBitcoinMerkleRoot(historical);

        cout << "Laukiama saknis: " << expected << endl;
        cout << "Istorinio testo rezultatas: "
             << (historicalRoot == expected ? "TEISINGAS" : "KLAIDA")
             << endl;

        vector<string> fiveLeaves = historical;

        fiveLeaves.push_back(
            "0000000000000000000000000000000000000000000000000000000000000000"
        );

        string fiveRoot = calculateBitcoinMerkleRoot(fiveLeaves);

        cout << "5 lapai: " << fiveRoot
             << " - "
             << (fiveRoot ==
                 "62e476d5f82f6bc8a981ce45a0368c5f5a81511e6f1606cf202348febb67ea84"
                 ? "TEISINGAS" : "KLAIDA")
             << endl;

        vector<string> changed = historical;

        changed[0][0] = changed[0][0] == '0' ? '1' : '0';

        cout << "Pakeistas lapas duoda kita sakni: "
             << (calculateBitcoinMerkleRoot(changed) != historicalRoot
                 ? "TAIP" : "NE")
             << endl;

        vector<string> swapped = historical;

        swap(swapped[0], swapped[1]);

        cout << "Sukeitus lapus gaunama kita saknis: "
             << (calculateBitcoinMerkleRoot(swapped) != historicalRoot
                 ? "TAIP" : "NE")
             << endl;

        cout << "Tuscio saraso testas: ";

        try
        {
            calculateBitcoinMerkleRoot({});
            cout << "KLAIDA" << endl;
        }
        catch (const exception&)
        {
            cout << "ATMESTAS" << endl;
        }

        cout << "Neteisingo HEX ilgio testas: ";

        try
        {
            calculateBitcoinMerkleRoot({ "1234" });
            cout << "KLAIDA" << endl;
        }
        catch (const exception&)
        {
            cout << "ATMESTAS" << endl;
        }

        cout << "Neteisingu HEX simboliu testas: ";

        try
        {
            calculateBitcoinMerkleRoot({
                "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            });

            cout << "KLAIDA" << endl;
        }
        catch (const exception&)
        {
            cout << "ATMESTAS" << endl;
        }

        cout << "Neteisingos baitu tvarkos testas: ";

        vector<string> reversed = historical;

        for (string& txid : reversed)
        {
            vector<string> bytes;

            for (size_t i = 0; i < txid.size(); i += 2)
            {
                bytes.push_back(txid.substr(i, 2));
            }

            reverse(bytes.begin(), bytes.end());

            txid.clear();

            for (const string& byte : bytes)
            {
                txid += byte;
            }
        }

        cout << (calculateBitcoinMerkleRoot(reversed) != historicalRoot
            ? "TAIP" : "NE") << endl;

        if (argc > 1)
        {
            ifstream file(argv[1]);

            if (!file)
            {
                throw runtime_error("Nepavyko atidaryti TXID failo.");
            }

            vector<string> txids;
            string txid;

            while (file >> txid)
            {
                txids.push_back(txid);
            }

            cout << "Failo " << argv[1] << " Merkle saknis: "
                 << calculateBitcoinMerkleRoot(txids)
                 << endl;
        }
    }
    catch (const exception& error)
    {
        cerr << "Klaida: " << error.what() << endl;
        return 1;
    }

    return 0;
}

