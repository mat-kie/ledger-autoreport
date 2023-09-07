FROM pandoc/latex
RUN mkdir /ledger-tools
ADD ./ledger-tools /ledger-tools
RUN apk add python3 ledger
ENTRYPOINT ["/bin/ash"]