echo accounts
./herodotus.py ../corp-list-accounts-api --name Listing-Accounts-Api --format html >> changelog.html
echo albo
./herodotus.py ../corp-list-albo-api --name Albo-Api --format html >> changelog.html
echo cards
./herodotus.py ../corp-list-cards-api --name Cards-Api --format html >> changelog.html
echo print
./herodotus.py ../corp-list-print-api --name Print-Api --format html >> changelog.html
echo transactions
./herodotus.py ../corp-list-transactions-api --name Transactions-Api --format html >> changelog.html
echo trend
./herodotus.py ../corp-list-trend-api --name Trend-Api --format html >> changelog.html
echo turnover
./herodotus.py ../corp-list-turnovers-api --name Turnovers-Api --format html >> changelog.html
echo accounts rpay
./herodotus.py ../corp-rpay-accounts-api --name RPay-Accounts-Api --format html >> changelog.html
echo catalogs
./herodotus.py ../corp-rpay-catalogs-api --name Catalogs-Api  --format html >> changelog.html
echo organizations
./herodotus.py ../corp-rpay-organizations-api --name Organizations-Api --format html >> changelog.html
echo profiles
./herodotus.py ../corp-rpay-profiles-api --name Profiles-Api --format html >> changelog.html
