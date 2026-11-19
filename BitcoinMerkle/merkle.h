#ifndef BITCOIN_MERKLE_H
#define BITCOIN_MERKLE_H

#include <string>
#include <vector>

std::string calculateBitcoinMerkleRoot(const std::vector<std::string>& txids);
bool isValidTxid(const std::string& txid);

#endif
