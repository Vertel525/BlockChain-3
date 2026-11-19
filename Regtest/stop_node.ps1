$datadir = Join-Path $HOME "bitcoin-regtest-mif"
bitcoin-cli.exe -regtest "-datadir=$datadir" stop
