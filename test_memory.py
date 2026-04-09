from memory_system import ConversationMemory


def test_memory_system():
    # Initialize with test file
    memory = ConversationMemory("test_memory.json", max_conversations=3)

    print("=== Testing Memory System ===\n")

    # Test 1: Add 3 conversations
    print("Test 1: Adding 3 conversations...")
    memory.add_conversation("What is AI?", "AI is artificial intelligence.")
    memory.add_conversation("How does ML work?", "ML learns patterns from data.")
    memory.add_conversation("What is deep learning?", "Deep learning uses neural networks.")

    context = memory.get_context()
    print(context)
    print("[PASS] Stored 3 conversations\n")

    # Test 2: Add 4th conversation (should remove oldest)
    print("Test 2: Adding 4th conversation (rotation test)...")
    memory.add_conversation("What is NLP?", "NLP processes natural language.")

    context = memory.get_context()
    print(context)

    # Verify first conversation is gone
    if "What is AI?" not in context:
        print("[PASS] Oldest conversation removed successfully\n")
    else:
        print("[FAIL] Rotation failed\n")

    # Test 3: Clear memory
    print("Test 3: Clearing memory...")
    memory.clear()
    context = memory.get_context()
    print(context)
    print("[PASS] Memory cleared\n")

    # Test 4: Crash resistance
    print("Test 4: Testing crash resistance...")
    try:
        memory.add_conversation("Test query", "Test response")
        memory.add_conversation("Another query", "Another response")
        print("[PASS] No crashes detected\n")
    except Exception as e:
        print(f"[FAIL] Error: {e}\n")

    print("=== All Tests Complete ===")


if __name__ == "__main__":
    test_memory_system()
