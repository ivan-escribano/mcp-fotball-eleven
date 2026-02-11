import secrets
import argparse
from sqlmodel import Session, SQLModel

from db.database import engine
from model import ApiKey
from auth.middleware import hash_api_key


def initialize_api_keys_table():
    """Create the api_keys table if it doesn't exist."""
    SQLModel.metadata.create_all(engine)


def create_api_key(name: str) -> str:
    """Generate a new API key and store its hash in the database."""
    raw_key = f"sk_{secrets.token_hex(24)}"

    key_hash = hash_api_key(raw_key)

    with Session(engine) as session:
        api_key = ApiKey(name=name, key_hash=key_hash)

        session.add(api_key)

        session.commit()

    return raw_key


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new API key")

    parser.add_argument("--name", required=True, help="Client/pilot name")

    args = parser.parse_args()

    initialize_api_keys_table()

    key = create_api_key(args.name)

    print("\n" + "=" * 50)
    print("API KEY CREATED - SAVE THIS, IT WON'T BE SHOWN AGAIN!")
    print("=" * 50)
    print(f"Name: {args.name}")
    print(f"Key:  {key}")
    print("=" * 50 + "\n")
