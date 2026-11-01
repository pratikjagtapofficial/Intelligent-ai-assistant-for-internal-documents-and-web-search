from main import agent


test_questions = [
    "How many annual leave days do employees receive?",

    "Find the official Python documentation URL.",

    "Compare our company's remote-work policy "
    "with current Indian regulations."
]


for question in test_questions:

    print("\n" + "=" * 60)
    print("USER QUESTION:", question)
    print("=" * 60)

    # Send the question to the agent.
    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    # Display the tools requested and executed.
    for message in response["messages"]:

        # An AI message may contain tool-call requests.
        tool_calls = getattr(message, "tool_calls", [])

        for tool_call in tool_calls:
            print("Agent requested tool:", tool_call["name"])

        # Tool messages contain the actual tool results.
        if getattr(message, "name", None):
            print("Tool executed:", message.name)

    # Display the final answer.
    print("\nFINAL ANSWER:")
    # Get the final message from the agent.
    final_message = response["messages"][-1]

    # Get its content.
    content = final_message.content

    # Gemini may return either a string or a list of blocks.
    if isinstance(content, str):
        final_answer = content
    else:
        final_answer = "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )

    print("\nFINAL ANSWER:")
    print(final_answer)