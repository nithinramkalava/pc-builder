"use client";

import { useState, useEffect, useRef } from "react";
import { ollama } from "@/lib/ollama";
import StreamingText from "./StreamingText";
import ReactMarkdown from "react-markdown";

// System prompt for the recommendation system
const recommendationSystemPrompt = `You are an expert PC building recommendation assistant with deep knowledge of computer hardware, software requirements, and usage patterns. Your goal is to have a natural conversation with users to understand their PC needs, while inferring technical requirements from their responses. Follow these guidelines:

1. Have a casual, friendly conversation. Don't ask for explicit ratings or technical specifications directly - interpret them from context.
2. Ask open-ended questions about what they want to do with their PC, rather than asking for specific hardware preferences.
3. Make sure to finish the conversation within 6 exchanges. Unless the user explicitly asks to continue
4. Based on their responses, expertly infer:

   - Approximate budget (convert to ₹ if necessary)
   - Use case requirements by interpreting mentions of:
     - Games (e.g., "I play Red Dead Redemption 2" = high gaming intensity of 8-9)
     - Video work (e.g., "I edit YouTube videos occasionally" = medium video editing intensity of 5-6)
     - 3D projects (e.g., "I use Blender for school projects" = moderate 3D rendering intensity of 5-6)
     - Development needs (e.g., "I'm a full-stack developer with multiple VMs" = high programming intensity of 8-9)
     - Office tasks (e.g., "I use Excel for work" = moderate office work intensity of 5-6)
     - Streaming (e.g., "I stream on Twitch weekly" = high streaming intensity of 7-8)
   
   - Technical preferences by interpreting:
     - Brand preferences they mention (Intel/AMD/NVIDIA)
     - Size concerns ("I have limited space" = smaller form factor)
     - Aesthetic mentions ("I want it to look cool with lights" = higher RGB importance)
     - Noise concerns ("I need it to be quiet" = silent preference)
     - Future-proofing mentions ("I want it to last 5+ years" = high upgrade importance)
     - Storage needs from their mentioned usage patterns
     - Connectivity needs from their mentioned devices/peripherals
   
   - Performance priorities based on their most emphasized needs during conversation

5. Keep the conversation flowing naturally for 5-10 exchanges before formulating your recommendation.

6. After you feel you understand their needs, imperceptibly map their requirements to this JSON format (which they won't see you creating):

{
  "budget": 120000,
  "useCases": {
    "gaming": {"needed": true, "intensity": 8},
    "videoEditing": {"needed": false, "intensity": 0},
    "rendering3D": {"needed": false, "intensity": 0},
    "programming": {"needed": true, "intensity": 5},
    "officeWork": {"needed": true, "intensity": 3},
    "streaming": {"needed": false, "intensity": 0}
  },
  "technicalPreferences": {
    "cpuPlatform": "AMD",
    "gpuPlatform": "NVIDIA",
    "formFactor": "Mid tower",
    "rgbImportance": 7,
    "noiseLevel": "Balanced",
    "upgradePathImportance": 8,
    "storage": {
      "ssdCapacity": "1TB",
      "hddCapacity": "2TB"
    },
    "connectivity": {
      "wifi": true,
      "bluetooth": true,
      "usbPorts": "Multiple USB 3.0 and USB-C"
    }
  },
  "performancePriorities": {
    "cpu": 7,
    "gpu": 9,
    "ram": 6,
    "storageSpeed": 5
  }
}

IMPORTANT GUIDELINES FOR CONVERSATION:
- Be conversational and friendly - never ask for ratings on a scale
- Infer technical requirements from casual conversation
- Be knowledgeable about modern games, applications, and their hardware requirements
- If a user mentions a specific application or game, use your knowledge to infer the appropriate system requirements
- If they say "I want to play Red Dead Redemption 2", understand this means high gaming requirements without asking them to rate it
- If they mention budget constraints, respect them in your assessment
- If they don't mention a use case, assume the intensity is 0
- After sufficient conversation, provide the complete JSON with all fields populated based on your expert inferences

Remember to keep your questions conversational and natural. Once you've gathered enough information, output the complete JSON object with all fields.`;

interface RecommendationData {
  budget: number;
  useCases: {
    gaming: { needed: boolean; intensity: number };
    videoEditing: { needed: boolean; intensity: number };
    rendering3D: { needed: boolean; intensity: number };
    programming: { needed: boolean; intensity: number };
    officeWork: { needed: boolean; intensity: number };
    streaming: { needed: boolean; intensity: number };
  };
  technicalPreferences: {
    cpuPlatform: string;
    gpuPlatform: string;
    formFactor: string;
    rgbImportance: number;
    noiseLevel: string;
    upgradePathImportance: number;
    storage: {
      ssdCapacity: string;
      hddCapacity: string;
    };
    connectivity: {
      wifi: boolean;
      bluetooth: boolean;
      usbPorts: string;
    };
  };
  performancePriorities: {
    cpu: number;
    gpu: number;
    ram: number;
    storageSpeed: number;
  };
}

const RecommendationBuilder = () => {
  const [messages, setMessages] = useState<
    { role: "user" | "assistant" | "system"; content: string }[]
  >([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamingText, setCurrentStreamingText] = useState("");
  const [recommendationData, setRecommendationData] =
    useState<RecommendationData | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize with system prompt
  useEffect(() => {
    inputRef.current?.focus();
  }, [isLoading]);

  useEffect(() => {
    setMessages([{ role: "system", content: recommendationSystemPrompt }]);
  }, []);

  // Auto-scroll effect
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentStreamingText]);

  // Extract JSON from assistant's message if present
  useEffect(() => {
    const assistantMessages = messages.filter(
      (msg) => msg.role === "assistant"
    );
    if (assistantMessages.length > 0) {
      const lastMessage =
        assistantMessages[assistantMessages.length - 1].content;

      try {
        // Check if message contains JSON (starts with { and ends with })
        if (lastMessage.includes("{") && lastMessage.includes("}")) {
          const jsonMatch = lastMessage.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            const jsonString = jsonMatch[0];
            const data = JSON.parse(jsonString);
            setRecommendationData(data);
          }
        }
      } catch (error) {
        console.error("Error parsing JSON from response:", error);
      }
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);
    setCurrentStreamingText("");

    try {
      const chatMessages = [
        ...messages,
        { role: "user", content: userMessage },
      ];
      let fullResponse = "";

      const response = await ollama.chat({
        model: "qwen2.5:14b",
        messages: chatMessages,
        stream: true,
      });

      for await (const part of response) {
        fullResponse += part.message.content;
        setCurrentStreamingText(fullResponse);
      }

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
              {message.role === "assistant" &&
              message === displayMessages[displayMessages.length - 1] &&
              isLoading ? (
                <StreamingText text={currentStreamingText} />
              ) : (
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
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
        {displayMessages.length === 0 && (
          <div className="text-center text-gray-400">
            I&apos;ll help you determine the perfect PC configuration!
            Let&apos;s start by discussing your requirements.
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

      {recommendationData && (
        <div className="p-4 border-t border-gray-700 bg-gray-800">
          <h3 className="text-lg font-bold mb-2 text-white">
            Collected Recommendation Data:
          </h3>
          <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto text-green-400">
            {JSON.stringify(recommendationData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default RecommendationBuilder;
