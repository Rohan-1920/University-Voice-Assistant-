from supabase_memory import SupabaseMemory


def test_supabase_integration():
    print("=== Testing Supabase Integration ===\n")

    # Initialize
    memory = SupabaseMemory()

    if memory.fallback_mode:
        print("[INFO] Running in fallback mode - Supabase not configured\n")
    else:
        print("[INFO] Connected to Supabase\n")

    # Test 1: Save conversations
    print("Test 1: Saving conversations...")
    students = ["S12345", "S67890"]

    for student_id in students:
        success1 = memory.save_conversation(
            student_id=student_id,
            user_query="What is Python?",
            ai_response="Python is a high-level programming language."
        )

        success2 = memory.save_conversation(
            student_id=student_id,
            user_query="How do I use loops?",
            ai_response="Use for loops to iterate over sequences."
        )

        if success1 and success2:
            print(f"[PASS] Saved conversations for {student_id}")
        else:
            print(f"[FAIL] Failed to save for {student_id}")

    print()

    # Test 2: Fetch history
    print("Test 2: Fetching conversation history...")
    for student_id in students:
        history = memory.fetch_history(student_id, limit=5)

        if history:
            print(f"[PASS] Fetched {len(history)} conversations for {student_id}")
            for i, conv in enumerate(history, 1):
                print(f"  {i}. Q: {conv['user_query'][:40]}...")
        else:
            print(f"[FAIL] No history found for {student_id}")

    print()

    # Test 3: Error handling
    print("Test 3: Testing error handling...")
    try:
        # Test with empty student ID
        result = memory.save_conversation("", "Test", "Test")
        print(f"[INFO] Empty student ID handled: {result}")

        # Test fetch with non-existent student
        history = memory.fetch_history("NONEXISTENT", limit=5)
        print(f"[PASS] Non-existent student handled: {len(history)} results")

    except Exception as e:
        print(f"[FAIL] Error handling failed: {e}")

    print("\n=== Tests Complete ===")


if __name__ == "__main__":
    test_supabase_integration()
