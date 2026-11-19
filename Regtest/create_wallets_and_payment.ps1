$datadir = Join-Path $HOME "bitcoin-regtest-mif"
$cli = "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe"
$pythonDir = Join-Path $PSScriptRoot "..\PythonAnalysis"

function Invoke-BitcoinCli {
    param([string[]]$Arguments)
    & $cli -regtest "-datadir=$datadir" @Arguments
    if ($LASTEXITCODE -ne 0) { throw "bitcoin-cli komanda nepavyko: $Arguments" }
}

$loadedWallets = @(Invoke-BitcoinCli @("listwallets") | ConvertFrom-Json)
$walletDirectory = Invoke-BitcoinCli @("listwalletdir") | ConvertFrom-Json
$existingWallets = @($walletDirectory.wallets | ForEach-Object { $_.name })

foreach ($walletName in @("MIF", "student")) {
    if ($loadedWallets -notcontains $walletName) {
        if ($existingWallets -contains $walletName) {
            Invoke-BitcoinCli @("loadwallet", $walletName) | Out-Null
        } else {
            Invoke-BitcoinCli @("-named", "createwallet", "wallet_name=$walletName", "load_on_startup=true") | Out-Null
        }
    }
}

$miner = Invoke-BitcoinCli @("-rpcwallet=MIF", "getnewaddress", "mining", "bech32")
$recipient = Invoke-BitcoinCli @("-rpcwallet=student", "getnewaddress", "payment", "bech32")

Write-Host "Generuojami 101 blokai..."
Invoke-BitcoinCli @("generatetoaddress", "101", $miner) | Out-Null
Invoke-BitcoinCli @("-rpcwallet=MIF", "getbalances")

$prevouts = Invoke-BitcoinCli @("-rpcwallet=MIF", "listunspent")
$prevouts | Set-Content -Encoding utf8 (Join-Path $pythonDir "prevouts.json")

Write-Host "Siunciamas 1 BTC mokėjimas..."
$txid = Invoke-BitcoinCli @("-rpcwallet=MIF", "-named", "sendtoaddress", "address=$recipient", "amount=1", "fee_rate=2")
$txid | Set-Content -Encoding ascii (Join-Path $pythonDir "payment_txid.txt")
Write-Host "TXID: $txid"
Write-Host "Mempool būsena prieš patvirtinimą:"
Invoke-BitcoinCli @("getmempoolinfo")
Invoke-BitcoinCli @("-rpcwallet=student", "gettransaction", $txid)

Write-Host "Generuojamas vienas blokas mokėjimui patvirtinti..."
Invoke-BitcoinCli @("generatetoaddress", "1", $miner) | Out-Null
$blockhash = Invoke-BitcoinCli @("getbestblockhash")
$blockhash | Set-Content -Encoding ascii (Join-Path $pythonDir "payment_blockhash.txt")
Write-Host "Patvirtintas blokas: $blockhash"
Invoke-BitcoinCli @("-rpcwallet=student", "gettransaction", $txid)
Invoke-BitcoinCli @("getmempoolinfo")

$raw = Invoke-BitcoinCli @("getrawtransaction", $txid, "false", $blockhash)
$decoded = Invoke-BitcoinCli @("decoderawtransaction", $raw)
$decoded | Set-Content -Encoding utf8 (Join-Path $pythonDir "decoded_payment.json")
Write-Host "Mokėjimo duomenys išsaugoti PythonAnalysis kataloge."
