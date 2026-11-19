#include "merkle.h"
#include <bitcoin/system.hpp>
#include <algorithm>
#include <stdexcept>

using namespace std;

bool isValidTxid(const string& txid)
{
    if (txid.length() != 64)
        return false;

    for (char c : txid)
    {
        if (!((c >= '0' && c <= '9') ||
              (c >= 'a' && c <= 'f') ||
              (c >= 'A' && c <= 'F')))
            return false;
    }

    return true;
}

static bc::hash_digest txidToBytes(const string& txid)
{
    if (!isValidTxid(txid))
        throw invalid_argument("TXID turi buti 64 hex simboliu.");

    bc::hash_digest result{};

    for (size_t i = 0; i < 32; i++)
    {
        string byteText = txid.substr(i * 2, 2);
        unsigned int value = stoul(byteText, nullptr, 16);
        result[31 - i] = static_cast<uint8_t>(value);
    }

    return result;
}

static string bytesToTxid(const bc::hash_digest& bytes)
{
    static const char digits[] = "0123456789abcdef";
    string result;
    result.reserve(64);

    for (int i = 31; i >= 0; i--)
    {
        result += digits[bytes[i] >> 4];
        result += digits[bytes[i] & 0x0f];
    }

    return result;
}

string calculateBitcoinMerkleRoot(const vector<string>& txids)
{
    if (txids.empty())
        throw invalid_argument("TXID sarasas negali buti tuscias.");

    vector<bc::hash_digest> level;

    for (const string& txid : txids)
        level.push_back(txidToBytes(txid));

    while (level.size() > 1)
    {
        if (level.size() % 2 != 0)
            level.push_back(level.back());

        vector<bc::hash_digest> nextLevel;

        for (size_t i = 0; i < level.size(); i += 2)
        {
            bc::data_chunk pair;
            pair.insert(pair.end(), level[i].begin(), level[i].end());
            pair.insert(pair.end(), level[i + 1].begin(), level[i + 1].end());
            nextLevel.push_back(bc::bitcoin_hash(pair));
        }

        level = nextLevel;
    }

    return bytesToTxid(level[0]);
}
