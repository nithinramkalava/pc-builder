// src/components/BeginnerBuilder.tsx
"use client";

import { useState, useEffect, useRef } from "react";
import { ollama, systemPrompt } from "@/lib/ollama";
import ReactMarkdown from "react-markdown";

const BeginnerBuilder = () => {
  const [messages, setMessages] = useState<
    { role: "user" | "assistant" | "system"; content: string }[]
  >([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize with system prompt
  useEffect(() => {
    inputRef.current?.focus();
  }, [isLoading]);

  useEffect(() => {
    setMessages([{ role: "system", content: systemPrompt }]);
  }, []);

  // Auto-scroll effect
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const chatMessages = [
        ...messages,
        { role: "user", content: userMessage },
      ];

      // Get response from LLM
      const response = await ollama.chat({
        model: "qwen2.5:14b",
        messages: chatMessages,
      });

      // Get the full response text
      const fullResponse = response.message.content;

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: fullResponse },
      ]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I encountered an error. Please make sure Ollama is running locally with the required model installed.",
        },
      ]);
    }

    setIsLoading(false);
  };

  const displayMessages = messages.filter((msg) => msg.role !== "system");

  return (
    <div className="flex flex-col h-[80vh] bg-gray-900">
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {displayMessages.map((message, index) => (
          <div
            key={index}
            className={`${
              message.role === "user"
                ? "bg-gray-800 ml-12"
                : "bg-gray-700 mr-12"
            } p-4 rounded-lg shadow-md`}
          >
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-2xl font-bold mb-4 text-white">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-xl font-bold mb-3 text-white">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-lg font-bold mb-2 text-white">
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => (
                    <p className="mb-4 text-gray-200">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc ml-6 mb-4 text-gray-200">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal ml-6 mb-4 text-gray-200">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => (
                    <li className="mb-1 text-gray-200">{children}</li>
                  ),
                  code: ({ children }) => (
                    <code className="bg-gray-800 px-1 py-0.5 rounded text-green-400">
                      {children}
                    </code>
                  ),
                  pre: ({ children }) => (
                    <pre className="bg-gray-800 p-4 rounded-lg overflow-x-auto mb-4">
                      {children}
                    </pre>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
        {displayMessages.length === 0 && (
          <div className="text-center text-gray-400">
            Start by telling me about your PC building needs and budget!
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 rounded bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-600 transition-colors duration-200"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default BeginnerBuilder;
