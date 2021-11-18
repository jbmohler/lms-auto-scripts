import tools


def create_account_types(client):
    payload = client.get("api/journal/new")
    acctable = payload.named_table("journal")
    accrow = acctable.rows[0]
    accrow.jrn_name = "General"

    client.put(
        "api/journal/{}", accrow.id, files={"journal": acctable.as_http_post_file()}
    )

    types = [
        dict(name="Asset", balance_sheet=True, debit=True),
        dict(name="Liability", balance_sheet=True, debit=False),
        dict(name="Equity", balance_sheet=True, debit=False),
        dict(name="Revenue", balance_sheet=False, debit=False),
        dict(name="Expense", balance_sheet=False, debit=True),
    ]

    for tt in types:
        payload = client.get("api/accounttype/new")
        acctable = payload.named_table("accounttype")
        atrow = acctable.rows[0]
        atrow.atype_name = tt["name"]
        atrow.balance_sheet = tt["balance_sheet"]
        atrow.debit = tt["debit"]

        client.put(
            "api/accounttype/{}",
            atrow.id,
            files={"accounttype": acctable.as_http_post_file()},
        )


ACCOUNTS = [
    {"name": "Cash", "atype": "Asset"},
    {"name": "Savings", "atype": "Asset"},
    {"name": "Visa", "atype": "Liability"},
    {"name": "Mortgage", "atype": "Liability"},
    {"name": "Net Worth", "atype": "Equity"},
    {"name": "Salary Wages", "atype": "Revenue"},
    {"name": "Groceries", "atype": "Expense"},
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

            client.put(
                f"/api/account/{temprow.id}",
                files={"account": account.as_http_post_file()},
            )

            accs[acctemp["name"]] = temprow


def create_initial_balances(client):
    # bank balances

    # mortgage

    pass


def create_biweekly_paycheck(client):
    pass


def create_weekly_groceries(client):
    pass


def create_monthly_mortgage(client):
    pass


def create_random_automotive(client):
    pass


def outer(f):
    creds = {"username": "fred cfo", "password": "pigeon"}
    with tools.lms_std_client(creds) as client:
        f(client)


def main():
    pass


if __name__ == "__main__":
    main()
