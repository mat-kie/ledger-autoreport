import sys
import subprocess

__version__ = "0.1"

class BalanceEntry:
    amount_col = (None, 20)
    account_col = (22, None)
    ledger_separator_col = 20

    def __init__(self, line: str):
        self.amount = line[:self.amount_col[1]].strip()
        self.account = line[self.account_col[0]:].strip()
        self.indent_level = len(
            line[self.account_col[0]:].rstrip().split("  "))-1


class BalanceParser:
    def __init__(self, out_file, args: list[str]):
        self.args = args
        self.out_file = out_file
        self.header = ""
        self.footer = "\n"

    def parseAccountString(text: str):
        vec = text.rstrip().split("  ")
        return len(vec)-2, vec[-1]

    def parse(self, lines: str):
        entries: list[BalanceEntry] = []
        for line in lines.splitlines():
            if "--------------------" == line.rstrip():
                break
            entries.append(BalanceEntry(line))
        out = ""
        for entry in entries:
            out +="- "
            for i in range(0,entry.indent_level):
                out += "\\quad "
            color = " \\color{black}"
            if "-" in entry.amount:
                color = " \\color{red}"
            out += f"{entry.account} \\hfill {color} {entry.amount} \\color{{black}} \\newline\n"
            
        return out

    def execute(self):
        ledger_process = subprocess.run(
            ["ledger", "bal"] + self.args,
            capture_output=True,
            encoding='utf-8')
        assert ledger_process.returncode == 0, f"the ledger command failed: stdout: {ledger_process.stdout}, stderr:{ledger_process.stderr}"
        with open(self.out_file, "w+") as f:
            f.write(self.parse(ledger_process.stdout))


class RegisterParser:
    def __init__(self, out_file, args: list[str], col_headers: list[str],
                 date_col_width=10,
                 payee_col_width=60,
                 account_col_width=70,
                 amount_col_width=40,
                 total_col_width=40,
                 code_col_width=7
                 ):
        assert len(col_headers) == 6, "the register has to have 6 columns!"
        self.out_file = out_file
        self.args = args
        self.code_headers = col_headers
        self.date_col_width = date_col_width
        self.payee_col_width = payee_col_width
        self.account_col_width = account_col_width
        self.amount_col_width = amount_col_width
        self.total_col_width = total_col_width
        self.code_col_width = code_col_width
        self.date_col = (0, date_col_width)
        self.code_col = (self.date_col[1] + 1,
                         self.date_col[1] + 1 + code_col_width)
        self.payee_col = (self.code_col[1] + 1,
                          self.code_col[1] + 1 + payee_col_width)
        self.account_col = (self.payee_col[1] + 1,
                            self.payee_col[1] + 1 + account_col_width)
        self.amount_col = (self.account_col[1] + 1,
                           self.account_col[1] + 1 + amount_col_width)
        self.sum_col = (self.amount_col[1] + 1,
                        self.amount_col[1] + 1 + total_col_width)

    def get_header(self):
        return f"""\\begin{{longtable}}{{|r | c || l | l | r | r |}} 
\hline
{self.code_headers[0]} & {self.code_headers[1]} & {self.code_headers[2]} & {self.code_headers[3]} & {self.code_headers[4]} & {self.code_headers[5]}   \\\\
\hline
"""

    @staticmethod
    def get_footer():
        return "\\end{longtable}"

    def _parse_entry(self, line: str):
        date = line[:self.date_col[1]].strip()
        code = line[self.code_col[0]:self.code_col[1]].strip()
        payee = line[self.payee_col[0]:self.payee_col[1]].strip()
        account = line[self.account_col[0]:self.account_col[1]].strip()
        amount = line[self.amount_col[0]:self.amount_col[1]].strip()
        sum = line[self.sum_col[0]:].strip()
        return (
            f"{code} & {date} & {payee} & {account} "
            f"& {amount} & {sum} \\\\\n\hline"
        )

    def parse(self, ledger_output: str):
        tex_string = self.get_header()
        for line in ledger_output.splitlines():
            tex_string += self._parse_entry(line) + '\n'
        return tex_string + self.get_footer()

    def execute(self):
        register_format = (
            "%(ansify_if(  ansify_if(justify(format_date(date), int(date_width)),"
            "green if color and date > today), bold if should_bold))"
            f" %(ansify_if(ansify_if(justify(truncated(code, {self.code_col_width}), {self.code_col_width})"
            f"+ \" \" + justify(truncated(payee, int(payee_width)-{self.code_col_width}), int(payee_width)-{self.code_col_width}),"
            "bold if color and !cleared and actual), bold if should_bold))"
            " %(ansify_if(ansify_if(justify(truncated(display_account, int(account_width),"
            "int(abbrev_len)), int(account_width)), blue if color),"
            "bold if should_bold))"
            " %(ansify_if(justify(scrub(display_amount), int(amount_width),"
            "3 + int(meta_width) + int(date_width) + int(payee_width)"
            " + int(account_width) + int(amount_width) + int(prepend_width),"
            "true, color), bold if should_bold))"
            " %(ansify_if(   justify(scrub(display_total), int(total_width),"
            "4 + int(meta_width) + int(date_width) + int(payee_width)"
            "+ int(account_width) + int(amount_width) + int(total_width)"
            "+ int(prepend_width), true, color),"
            "bold if should_bold))\\n"
            "%/%(justify(\" \", int(date_width)))"
            " %(ansify_if(   justify(truncated(has_tag(\"Payee\")"
            f"? \"{' '*(self.code_col_width+1)}\" + payee : \" \", int(payee_width)), int(payee_width)),"
            "bold if should_bold)) %$3 %$4 %$5\\n"
        )
        additional_reg_args = [
            "--date-width", str(self.date_col_width), "--payee-width", str(
                self.payee_col_width + self.code_col_width + 1), "--account-width", str(self.account_col_width),
            "--amount-width", str(self.amount_col_width), "--total-width", str(
                self.total_col_width)
        ]
        ledger_process = subprocess.run(
            ["ledger"] + ["--format",
                          register_format, "reg"] + additional_reg_args + self.args,
            capture_output=True,
            encoding='utf-8')
        assert ledger_process.returncode == 0, f"the ledger command failed: stdout: {ledger_process.stdout}, stderr:{ledger_process.stderr}"
        with open(self.out_file, "w+") as f:
            f.write(self.parse(ledger_process.stdout))


if __name__ == '__main__':
    if "help" in sys.argv:
        print(
            f"""python ledger report latex generator ledger2latex {__version__}.
Usage: 
  python generate_reports.py < my_config.cfg.
  Config file format:
  register_columns: [code_title]; [date_title]; [payee_title]; [account_title]; [amount_title]; [sum_title]
  [out_file];[bal|reg];[ledger_args]
  ...
"""
        )
    elif "version" in sys.argv:
        print(f"ledger2latex version {__version__}")
    else:
        headers = None
        head_keyword = "register_columns:"
        a = [1, 2]
        for line in sys.stdin:
            if line.startswith(head_keyword):
                headers = [
                    entry.rstrip().lstrip()
                    for entry in line[len(head_keyword):].split(";")
                ]
            else:
                args = [x.rstrip().lstrip() for x in line.split(";")]
                assert len(
                    args) > 2, "you have to at least spec the output and type!"
                type = None
                if args[1] in ["reg", "register"]:
                    RegisterParser(args[0], args[2:], headers).execute()
                elif args[1] in ["bal", "balance"]:
                    BalanceParser(args[0], args[2:]).execute()
