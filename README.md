# ledger-autoreport
Tools to generate latex reports with ledger. 
Packaged as a simple dockerfile for a container with pandoc/latex python and the python scripts from ./ledger-tools.

# Build
take a look at ./build_container.sh to build the container with podman.

# Usage
1. have the container available on your system (build / pull it).
2. create a config file in your working directory of choice.
3. run  python3 /ledger-tools/ledger2latex.py < yourConfig.cfg in the container.
4. you can include the generated .tex files in your report latex file
5. run pdflatex in the container on your report.

# Config file for ledger2latex.py
A text file declaring the column headers for the register report type and
the lists of reports to generate.

~~~
register_columns: [code_title]; [date_title]; [payee_title]; [account_title]; [amount_title]; [sum_title]
[out_file];[bal|reg];[ledger_args]
...
~~~

example:

~~~
register_columns: Booking Code; Date; Payee; Account; Amount; Total
journal.tex; reg; -f; jourLedgerJournalFile.ledger
balance.tex; bal; -f; jourLedgerJournalFile.ledger;-E; Spendings
~~~
# podman shell command
to run the container in interactive mode:

~~~bash
podman run --rm -it --volume "$(pwd):/data" --userns keep-id --user $(id -u):$(id -g) finance/autoreport 
~~~
**Note:** The current working directory is mounted to /data inside the container. The ledger-tools folder is copied to /ledger-tools inside the container during the build step for the container.