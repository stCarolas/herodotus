echo accounts
./herodotus.py ../corp-list-accounts-api --name Listing-Accounts-Api --format confluence --toDate=18.05.2016>> changelog.html
echo albo
./herodotus.py ../corp-list-albo-api --name Albo-Api --format confluence  --toDate=18.05.2016 >> changelog.html
echo cards
./herodotus.py ../corp-list-cards-api --name Cards-Api --format confluence --toDate=18.05.2016 >> changelog.html
echo print
./herodotus.py ../corp-list-print-api --name Print-Api --format confluence --toDate=18.05.2016 >> changelog.html
echo transactions
./herodotus.py ../corp-list-transactions-api --name Transactions-Api --format confluence --toDate=18.05.2016 >> changelog.html
echo trend
./herodotus.py ../corp-list-trend-api --name Trend-Api --format confluence --toDate=18.05.2016 >> changelog.html
echo turnover
./herodotus.py ../corp-list-turnovers-api --name Turnovers-Api --format confluence --toDate=18.05.2016 >> changelog.html
echo accounts rpay
./herodotus.py ../corp-rpay-accounts-api --name RPay-Accounts-Api --format confluence --toDate=18.05.2016 >> changelog.html
echo catalogs
./herodotus.py ../corp-rpay-catalogs-api --name Catalogs-Api  --format confluence --toDate=18.05.2016 >> changelog.html
echo organizations
./herodotus.py ../corp-rpay-organizations-api --name Organizations-Api --format confluence --toDate=18.05.2016 >> changelog.html
echo profiles
./herodotus.py ../corp-rpay-profiles-api --name Profiles-Api --format confluence --toDate=18.05.2016 >> changelog.html
