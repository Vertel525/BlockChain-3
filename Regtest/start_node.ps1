$bitcoinDir = "C:\Program Files\Bitcoin\daemon"
$bitcoinCli = Join-Path $bitcoinDir "bitcoin-cli.exe"
$bitcoind = Join-Path $bitcoinDir "bitcoind.exe"

$datadir = Join-Path $HOME "bitcoin-regtest-mif"
New-Item -ItemType Directory -Force -Path $datadir | Out-Null

Write-Host "Regtest duomenu katalogas: $datadir"

& $bitcoinCli -regtest "-datadir=$datadir" getblockchaininfo 2>$null | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Paleidziamas Bitcoin Core regtest mazgas..."
    Start-Process -FilePath $bitcoind -ArgumentList @("-regtest", "-datadir=$datadir") -WindowStyle Hidden
}
else {
    Write-Host "Regtest mazgas jau veikia - antras procesas nepaleidziamas."
}
