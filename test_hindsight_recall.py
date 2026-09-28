from hindsight_memory import recall_vendor_history


def test_vendor(query, vendor_name, expected_keywords):
    print()
    print("=" * 60)
    print(f"Testing: {vendor_name}")
    print("=" * 60)

    memories = recall_vendor_history(
        query=query,
        vendor_name=vendor_name
    )

    if not memories:
        print("❌ No memories found.")
        return False

    print("Recalled memories:")

    for memory in memories:
        print(f"- {memory}")

    combined = " ".join(memories).lower()

    missing = []

    for keyword in expected_keywords:
        if keyword.lower() not in combined:
            missing.append(keyword)

    if missing:
        print()
        print(f"❌ Missing keywords: {missing}")
        return False

    print()
    print("✅ Test passed.")
    return True


def main():
    results = []

    results.append(
        test_vendor(
            query="What happened with the delayed PCB shipment and how did the vendor respond when we pushed back?",
            vendor_name="Nexus Components",
            expected_keywords=[
                "14 days",
                "12%",
                "Meridian"
            ]
        )
    )

    results.append(
        test_vendor(
            query="What happened when this vendor increased its price, and what negotiation tactic worked?",
            vendor_name="Solvex Chemicals",
            expected_keywords=[
                "BlueRock",
                "4%",
                "competing quote"
            ]
        )
    )

    results.append(
        test_vendor(
            query="What is this vendor's delivery and quality history?",
            vendor_name="Apex Logistics",
            expected_keywords=[
                "98.6%",
                "zero quality",
                "on-time"
            ]
        )
    )

    print()
    print("=" * 60)
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    main()