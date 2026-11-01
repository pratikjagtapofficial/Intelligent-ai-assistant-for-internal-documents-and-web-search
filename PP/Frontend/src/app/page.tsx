"use client";

import { useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";


// ============================================================
// 1. TYPES
// ============================================================

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatResponse {
  answer: string;
}

function isChatResponse(value: unknown): value is ChatResponse {
  return (
    typeof value === "object" &&
    value !== null &&
    "answer" in value &&
    typeof value.answer === "string"
  );
}


// ============================================================
// 2. MAIN COMPONENT
// ============================================================

export default function Home() {

  // ==========================================================
  // 2.1 STATE
  // ==========================================================

  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const sessionIdRef = useRef<string | null>(null);

  const getSessionId = (): string => {
    if (!sessionIdRef.current) {
      sessionIdRef.current = crypto.randomUUID();
    }

    return sessionIdRef.current;
  };


  // ==========================================================
  // 2.2 NEW CHAT
  // ==========================================================

  const startNewChat = (): void => {
    setMessages([]);
    setMessage("");
    sessionIdRef.current = null;
  };


  // ==========================================================
  // 2.3 SEND MESSAGE
  // ==========================================================

  const sendMessage = async (): Promise<void> => {
    const currentMessage = message.trim();

    if (!currentMessage || loading) {
      return;
    }

    // Add user message immediately
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: currentMessage,
      },
    ]);

    setMessage("");
    setLoading(true);


    // ========================================================
    // 2.4 API CALL → FASTAPI
    // ========================================================

    try {
      const result = await fetch("/api/chat", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          question: currentMessage,
          session_id: getSessionId(),
        }),
      });


      if (!result.ok) {
        let errorMessage = `Request failed with status ${result.status}.`;

        try {
          const errorData: { detail?: unknown } = await result.json();
          if (typeof errorData.detail === "string") {
            errorMessage = errorData.detail;
          }
        } catch {
          // Keep the status-based message when the response is not JSON.
        }

        throw new Error(errorMessage);
      }


      // ======================================================
      // 2.5 RECEIVE RESPONSE
      // ======================================================

      const data: unknown = await result.json();
      if (!isChatResponse(data)) {
        throw new Error("The AI service returned an invalid response.");
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);

    } catch (error) {
      console.error("Chat error:", error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: error instanceof Error
            ? `Sorry, the AI service request failed: ${error.message}`
            : "Sorry, I couldn't connect to the AI service.",
        },
      ]);

    } finally {
      setLoading(false);
    }
  };


  // ==========================================================
  // 2.6 HANDLE ENTER KEY
  // ==========================================================

  const handleKeyDown = (
    event: KeyboardEvent<HTMLTextAreaElement>
  ): void => {

    // Enter → send
    // Shift + Enter → new line
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };


  // ==========================================================
  // 3. UI
  // ==========================================================

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4 md:px-6">
          <div>
            <h2 className="text-sm font-semibold text-gray-900 md:text-base">
              Company AI Assistant
            </h2>
            <p className="text-xs text-gray-500">
              Company policies + web search
            </p>
          </div>

          <button
            type="button"
            onClick={startNewChat}
            disabled={loading}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            New Chat
          </button>
        </header>
        <section className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="mx-auto flex min-h-full max-w-3xl flex-col items-center justify-center px-5 py-12">
              <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-900 text-sm font-bold text-white shadow-sm">
                AI
              </div>
              <h2 className="text-center text-2xl font-semibold tracking-tight text-gray-900 md:text-3xl">
                How can I help you?
              </h2>
              <p className="mt-3 max-w-xl text-center text-sm leading-6 text-gray-500">
                Ask about company policies, employee guidelines,
                or current information from the web.
              </p>
              <div className="mt-8 grid w-full gap-3 sm:grid-cols-2">
                <button
                  type="button"
                  onClick={() =>
                    setMessage(
                      "What is our company's WFH policy?"
                    )
                  }
                  className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50"
                >
                  <p className="font-medium text-gray-900">
                    WFH Policy
                  </p>

                  <p className="mt-1 text-xs leading-5 text-gray-500">
                    What is our company's WFH policy?
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setMessage(
                      "How many annual leave days do employees get?"
                    )
                  }
                  className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50"
                >
                  <p className="font-medium text-gray-900">
                    Leave Policy
                  </p>

                  <p className="mt-1 text-xs leading-5 text-gray-500">
                    How many annual leave days do employees get?
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setMessage(
                      "What benefits are available to employees?"
                    )
                  }
                  className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50"
                >
                  <p className="font-medium text-gray-900">
                    Employee Benefits
                  </p>

                  <p className="mt-1 text-xs leading-5 text-gray-500">
                    What benefits are available to employees?
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setMessage(
                      "Compare our WFH policy with current Indian regulations."
                    )
                  }
                  className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:border-gray-300 hover:bg-gray-50"
                >
                  <p className="font-medium text-gray-900">
                    Policy + Web
                  </p>

                  <p className="mt-1 text-xs leading-5 text-gray-500">
                    Compare our policy with current regulations.
                  </p>
                </button>
              </div>
            </div>
          ) : (
            <div className="mx-auto max-w-3xl px-5 py-8">
              {messages.map((chatMessage, index) => (
                <div
                  key={index}
                  className="mb-8 flex gap-3 md:gap-4"
                >
                  <div
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-semibold ${
                      chatMessage.role === "user"
                        ? "bg-gray-200 text-gray-700"
                        : "bg-gray-900 text-white"
                    }`}
                  >
                    {chatMessage.role === "user"
                      ? "U"
                      : "AI"}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="mb-1 text-xs font-semibold text-gray-500">
                      {chatMessage.role === "user"
                        ? "You"
                        : "Company AI"}
                    </p>
                    {chatMessage.role === "assistant" ? (
                      <div className="text-sm leading-7 text-gray-800 [&_a]:text-blue-700 [&_a]:underline [&_blockquote]:border-l-2 [&_blockquote]:border-gray-300 [&_blockquote]:pl-4 [&_code]:rounded [&_code]:bg-gray-100 [&_code]:px-1 [&_code]:py-0.5 [&_h1]:mb-2 [&_h1]:text-lg [&_h1]:font-semibold [&_h2]:mb-2 [&_h2]:text-base [&_h2]:font-semibold [&_hr]:my-4 [&_hr]:border-gray-200 [&_li]:ml-5 [&_li]:list-disc [&_ol_li]:list-decimal [&_p]:mb-3 [&_p:last-child]:mb-0 [&_pre]:my-3 [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-gray-100 [&_pre]:p-3 [&_strong]:font-semibold [&_ul]:mb-3">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {chatMessage.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap text-sm leading-7 text-gray-800">
                        {chatMessage.content}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex gap-3 md:gap-4">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-900 text-xs font-semibold text-white">
                    AI
                  </div>
                  <div>
                    <p className="mb-1 text-xs font-semibold text-gray-500">
                      Company AI
                    </p>
                    <div className="flex items-center gap-1 pt-1">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.3s]"></span>
                      <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.15s]"></span>
                      <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400"></span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
        <div className="border-t border-gray-200 bg-gray-50 px-4 py-4 md:px-6">
          <div className="mx-auto max-w-3xl">
            <div className="rounded-2xl border border-gray-300 bg-white p-2 shadow-sm transition focus-within:border-gray-400 focus-within:ring-2 focus-within:ring-gray-100">
              <div className="flex items-end gap-2">
                <textarea
                  value={message}
                  rows={1}
                  placeholder="Ask about company policies or search the web..."
                  onChange={(event) => setMessage(event.target.value)}
                  onKeyDown={handleKeyDown}
                  className="max-h-40 min-h-[44px] flex-1 resize-none border-0 bg-transparent px-3 py-2.5 text-sm text-gray-900 outline-none placeholder:text-gray-400"
                />
                <button
                  type="button"
                  onClick={sendMessage}
                  disabled={!message.trim() || loading}
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-900 text-lg text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-30"
                  aria-label="Send message"
                >
                  ↑
                </button>
              </div>
            </div>
            <p className="mt-2 text-center text-[11px] text-gray-400">
              Enter to send · Shift + Enter for a new line
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}