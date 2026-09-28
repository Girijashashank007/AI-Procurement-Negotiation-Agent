import json

from hindsight_memory import (
    verify_connection,
    store_vendor_history
)


DATA_FILE = "vendor_data.json"


def main():
    # Load vendor data
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        vendors = json.load(file)

    print(f"Found {len(vendors)} vendor records.")

    # Make sure Hindsight is connected
    verify_connection()

    # Upload each vendor record
    successful = 0

    for index, vendor in enumerate(vendors, start=1):
        try:
            store_vendor_history(
                vendor_name=vendor["vendor_name"],
                content=vendor["content"],
                context=vendor["context"],
                timestamp=vendor["timestamp"]
            )

            successful += 1
            print(
                f"[{index}/{len(vendors)}] "
                f"Uploaded: {vendor['vendor_name']}"
            )

        except Exception as e:
            print(
                f"[{index}/{len(vendors)}] "
                f"FAILED: {vendor['vendor_name']}"
            )
            print(f"Error: {e}")

    print()
    print(f"Successfully stored {successful}/{len(vendors)} vendor records.")


if __name__ == "__main__":
    main()