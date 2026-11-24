#!/usr/bin/env python3
import os
import sys

ACCOUNTS_PATH = os.path.join("data", "ACCOUNTS.DAT")
BOOKS_PATH = os.path.join("data", "BOOKS.DAT")
TRANSACTIONS_PATH = os.path.join("data", "TRANSACTIONS.DAT")
INPUT_PATH = os.path.join("src", "INPUT.DAT")

ACCOUNT_RECORD_SIZE = 4 + 20 + 10
BOOK_RECORD_SIZE = 4 + 20 + 4
TRANSACTION_RECORD_SIZE = 4 + 10 + 4 + 4
INPUT_RECORD_SIZE = 4 + 4 + 4 + 10


def read_input():
    with open(INPUT_PATH, "rb") as f:
        data = f.read()
    if len(data) == 0:
        print("Error: Input file is empty")
        sys.exit(0)
    if len(data) < INPUT_RECORD_SIZE:
        data = data + b" " * (INPUT_RECORD_SIZE - len(data))
    buyer = data[0:4]
    seller = data[4:8]
    book = data[8:12]
    amount_bytes = data[12:22]
    try:
        amount = int(amount_bytes.decode("ascii", errors="replace"))
    except ValueError:
        digits = b"".join(c.to_bytes(1, "big") for c in amount_bytes if 0x30 <= c <= 0x39)
        amount = int(digits) if digits else 0
    return buyer, seller, book, amount


def read_records(path, size):
    with open(path, "rb") as f:
        data = f.read()
    return [data[i:i + size] for i in range(0, len(data), size) if len(data[i:i + size]) == size]


def write_records(path, records):
    with open(path, "wb") as f:
        for r in records:
            f.write(r)


def main():
    buyer, seller, book, amount = read_input()

    accounts = read_records(ACCOUNTS_PATH, ACCOUNT_RECORD_SIZE)
    books = read_records(BOOKS_PATH, BOOK_RECORD_SIZE)

    buyer_found = any(r[0:4] == buyer for r in accounts)
    seller_found = any(r[0:4] == seller for r in accounts)
    book_found = False
    valid_owner = False
    for r in books:
        if r[0:4] == book:
            book_found = True
            if r[24:28] == seller:
                valid_owner = True

    if not (buyer_found and seller_found and book_found and valid_owner):
        print("Transaction failed due to validation errors")
        return

    new_accounts = []
    for r in accounts:
        acc_id = r[0:4]
        name = r[4:24]
        balance = int(r[24:34].decode("ascii"))
        if acc_id == buyer:
            balance = balance - amount
        if acc_id == seller:
            balance = balance + amount
        balance_str = f"{balance % 10**10:010d}".encode("ascii")
        new_accounts.append(acc_id + name + balance_str)
    write_records(ACCOUNTS_PATH, new_accounts)

    new_books = []
    for r in books:
        book_id = r[0:4]
        title = r[4:24]
        owner = r[24:28]
        if book_id == book:
            owner = buyer
        new_books.append(book_id + title + owner)
    write_records(BOOKS_PATH, new_books)

    trans_record = book + f"{amount:010d}".encode("ascii") + seller + buyer
    with open(TRANSACTIONS_PATH, "ab") as f:
        f.write(trans_record)

    print("Transaction completed successfully")


if __name__ == "__main__":
    main()
