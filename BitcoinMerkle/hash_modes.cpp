#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <cstdint>
#include <bitcoin/system.hpp>

using namespace std;

// Ankstesnio projekto mokomoji hash funkcija.
uint32_t rotateLeft(uint32_t value, int bits)
{
    return (value << bits) | (value >> (32 - bits));
}

string educationalHash(string text)
{
    uint32_t h[8] = {
        0x12345678, 0x23456789,
        0x34567890, 0x45678901,
        0x56789012, 0x67890123,
        0x78901234, 0x89012345
    };

    for (int i = 0; i < (int)text.length(); i++)
    {
        unsigned char c = (unsigned char)text[i];

        for (int j = 0; j < 8; j++)
        {
            h[j] = h[j] ^ (c + i + j * 17);
            h[j] = h[j] * 2654435761u;
            h[j] = rotateLeft(h[j], (j + 5) % 31 + 1);
            h[j] = h[j] ^ h[(j + 1) % 8];
        }
    }

    for (int j = 0; j < 8; j++)
    {
        h[j] = h[j] ^ (uint32_t)text.length();
        h[j] = h[j] * 2246822519u;
        h[j] = rotateLeft(h[j], 13);
    }

    stringstream result;

    for (int i = 0; i < 8; i++)
        result << hex << setw(8) << setfill('0') << h[i];

    return result.str();
}

// Bitcoin SHA256d: du kartus atliekama SHA-256.
string bitcoinHash(const string& text)
{
    bc::data_chunk data(text.begin(), text.end());
    bc::hash_digest digest = bc::bitcoin_hash(data);

    return bc::encode_hash(digest);
}

int main()
{
    int choice;
    string input;

    cout << "MAISOS FUNKCIJU REZIMAI" << endl;
    cout << "1 - Mokomoji hash funkcija" << endl;
    cout << "2 - Bitcoin SHA256d" << endl;
    cout << "0 - Iseiti" << endl;

    cout << "\nPasirinkimas: ";
    cin >> choice;

    if (choice == 0)
        return 0;

    if (choice != 1 && choice != 2)
    {
        cout << "Neteisingas pasirinkimas." << endl;
        return 1;
    }

    cin.ignore();

    cout << "Iveskite duomenis: ";
    getline(cin, input);

    if (choice == 1)
    {
        cout << "\nNaudojama mokomoji hash funkcija." << endl;
        cout << "Rezultatas: " << educationalHash(input) << endl;
    }
    else
    {
        cout << "\nNaudojama Bitcoin SHA256d." << endl;
        cout << "Rezultatas: " << bitcoinHash(input) << endl;
    }

    return 0;
}
