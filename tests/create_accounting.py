import random
import datetime
import tools


def create_account_types(client):
    payload = client.get("api/journal/new")
    acctable = payload.named_table("journal")
    accrow = acctable.rows[0]
    accrow.jrn_name = "General"

    client.put("api/journal/{}", accrow.id, tables={"journal": acctable})

    types = [
        dict(name="Asset", balance_sheet=True, debit=True, sort=10),
        dict(name="Liability", balance_sheet=True, debit=False, sort=20),
        dict(name="Equity", balance_sheet=True, debit=False, sort=30),
        dict(name="Revenue", balance_sheet=False, debit=False, sort=50),
        dict(name="Expense", balance_sheet=False, debit=True, sort=70),
    ]

    for tt in types:
        payload = client.get("api/accounttype/new")
        acctable = payload.named_table("accounttype")
        atrow = acctable.rows[0]
        atrow.atype_name = tt["name"]
        atrow.balance_sheet = tt["balance_sheet"]
        atrow.debit = tt["debit"]
        atrow.sort = tt["sort"]

        client.put("api/accounttype/{}", atrow.id, tables={"accounttype": acctable})


ACCOUNTS = [
    {"name": "Cash", "atype": "Asset"},
    {"name": "Savings", "atype": "Asset"},
    {"name": "House", "atype": "Asset"},
    {"name": "Visa", "atype": "Liability"},
    {"name": "Mortgage", "atype": "Liability"},
    {"name": "Net Worth", "atype": "Equity"},
    {"name": "Salary Wages", "atype": "Revenue"},
    {"name": "Groceries", "atype": "Expense"},
    {"name": "Taxes", "atype": "Expense"},
    {"name": "Transportation", "atype": "Expense"},
    {"name": "Interest/Fees", "atype": "Expense"},
]


def create_accounts(client):
    payload = client.get("/api/accounts/list")
    existing = payload.main_table()
    accs = {r.account: r for r in existing.rows}

    payload = client.get("/api/accounttypes/list")
    existing = payload.main_table()
    types = {r.atype_name: r for r in existing.rows}

    payload = client.get("/api/journals/list")
    existing = payload.main_table()
    journals = {r.jrn_name: r for r in existing.rows}

    for acctemp in ACCOUNTS:
        if acctemp["name"] not in accs:
            payload = client.get("api/account/new")
            account = payload.main_table()
            temprow = account.rows[0]
            temprow.acc_name = acctemp["name"]
            temprow.type_id = types[acctemp["atype"]].id
            temprow.journal_id = journals["General"].id
            if not types[acctemp["atype"]].balance_sheet:
                temprow.retearn_id = accs["Net Worth"].id

            client.put(f"/api/account/{temprow.id}", tables={"account": account})

            accs[acctemp["name"]] = temprow


def _trans(client, date, payee=None, memo=None, ref=None, split_accs=None):
    payload = client.get("/api/transaction/new")
    trans = payload.named_table("trans")
    splits = payload.named_table("splits")

    tranrow = trans.rows[0]
    tranrow.trandate = date
    tranrow.payee = payee
    tranrow.memo = memo
    tranrow.tranref = ref

    balance = sum({dc for dc in split_accs.values() if dc != "balance"})

    for accname, dc in split_accs.items():
        payload = client.get("/api/accounts/completions", prefix=accname)
        accounts = payload.named_table("accounts")

        assert (
            len(accounts.rows) == 1
        ), f"The account name {accname} is ambiguous or unknown"

        with splits.adding_row() as r2:
            r2.account_id = accounts.rows[0].id
            r2.sum = dc if dc != "balance" else -balance

    client.put(
        f"/api/transaction/{tranrow.tid}", tables={"trans": trans, "splits": splits}
    )


def _print_balance_sheet(client):
    jan1 = anchor_jan1()
    payload = client.get("/api/gledger/balance-sheet", date=f"{jan1.year}-12-31")
    balances = payload.main_table()

    print("*** balance sheet ***")
    for h in payload.keys['headers']:
        print(h)
    balances.rows.sort(key=lambda x: (x.atype_sort, x.acc_name))
    for row in balances.rows:
        print(f"{row.atype_name:<20s} {row.acc_name:<20s} {row.balance:9.2f}")
        # print(f"{row.atype_name:<20s} {row.acc_name:<20s} {row.debit:9.2f} {row.credit:9.2f}")

def _print_p_and_l(client):
    jan1 = anchor_jan1()
    payload = client.get("/api/gledger/profit-and-loss", date1=f"{jan1.year}-01-01", date2=f"{jan1.year}-12-31")
    balances = payload.main_table()

    print("*** profit & loss ***")
    for h in payload.keys['headers']:
        print(h)
    balances.rows.sort(key=lambda x: (x.atype_sort, x.acc_name))
    for row in balances.rows:
        print(f"{row.atype_name:<20s} {row.acc_name:<20s} {row.balance:9.2f}")
        # print(f"{row.atype_name:<20s} {row.acc_name:<20s} {row.debit:9.2f} {row.credit:9.2f}")


def anchor_jan1():
    today = datetime.date.today()
    return datetime.date(today.year - 1, 1, 1)


def create_initial_balances(client):
    jan1 = anchor_jan1()

    # bank balances
    _trans(
        client,
        date=jan1 - datetime.timedelta(days=1),
        memo="Beginning Balance",
        split_accs={
            "Cash": 125,
            "Savings": 15000,
            "Visa": -500,
            "Net Worth": "balance",
        },
    )

    # mortgage
    _trans(
        client,
        date=jan1 - datetime.timedelta(days=1),
        memo="Beginning Balance",
        split_accs={
            "House": 175000,
            "Mortgage": -95000,
            "Net Worth": "balance",
        },
    )

    _print_balance_sheet(client)


def create_biweekly_paycheck(client):
    jan1 = anchor_jan1()

    # arbitrarily choose Jan 5
    first = jan1 + datetime.timedelta(days=4)

    # bank balances
    for i in range(26):
        _trans(
            client,
            date=first + datetime.timedelta(days=i*14),
            memo="Paycheck",
            split_accs={
                "Salary Wages": -3500,
                "Taxes": 454.23,
                "Savings": "balance",
            },
        )


def create_weekly_groceries(client):
    jan1 = anchor_jan1()

    offsets = random.sample(list(range(365)), 52)
    for i in offsets:
        _trans(
            client,
            date=jan1+datetime.timedelta(days=i),
            payee=random.choice(['Giant', 'Aldi']),
            memo="Groceries",
            split_accs={
                "Groceries": round(random.gammavariate(120, 60), 2),
                "Visa": "balance",
            },
        )


def create_monthly_mortgage(client):
    jan1 = anchor_jan1()

    for i in range(12):
        _trans(
            client,
            date=datetime.date(jan1.year, i+1, 5),
            payee="First Spunky Bank",
            memo="Mortgage",
            split_accs={
                "Mortgage": 650.23,
                "Interest/Fees": "balance",
                "Savings": -967.23,
            },
        )


def create_random_automotive(client):
    jan1 = anchor_jan1()

    # gas expense
    offsets = random.sample(list(range(365)), 20)
    for i in offsets:
        _trans(
            client,
            date=jan1+datetime.timedelta(days=i),
            payee=random.choice(['Exxon', 'WaWa', 'BP']),
            memo="Gas",
            split_accs={
                "Transportation": round(random.gammavariate(25, 5), 2),
                "Visa": "balance",
            },
        )

    # repairs expense
    offsets = random.sample(list(range(365)), 8)
    for i in offsets:
        _trans(
            client,
            date=jan1+datetime.timedelta(days=i),
            payee="Joe's Garage",
            memo="Repaired Car",
            split_accs={
                "Transportation": round(random.gammavariate(85, 15), 2),
                "Visa": "balance",
            },
        )

    _print_balance_sheet(client)
    _print_p_and_l(client)

def outer(f):
    creds = {"username": "fred cfo", "password": "pigeon"}
    with tools.lms_std_client(creds) as client:
        f(client)


def main():
    pass


if __name__ == "__main__":
    main()
