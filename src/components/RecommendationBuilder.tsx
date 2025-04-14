"use client";

import { useState, useEffect, useRef } from "react";
import { ollama } from "@/lib/ollama";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import LoadingScreen from "./LoadingScreen";
import BuildResultDisplay, { BuildRecommendation } from "./BuildResultDisplay";

// System prompt for the recommendation system
const recommendationSystemPrompt = `You are an expert PC building recommendation assistant with deep knowledge of computer hardware, software requirements, and usage patterns. Your goal is to have a natural conversation with users to understand their PC needs, while inferring technical requirements from their responses. Follow these guidelines:
0. DO NOT HALLUCINATE ALWAYS STRICTLY FOLLOW THE INSTRUCTIONS
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
     - Market segment needs ("I need it for professional work" = Workstation, vs regular use = Consumer)
     - Size concerns ("I have limited space" = smaller form factor)
     - Aesthetic mentions ("I want it to look cool with lights" = higher RGB importance)
     - Noise concerns ("I need it to be quiet" = silent preference)
     - Future-proofing mentions ("I want it to last 5+ years" = high upgrade importance)
     - Storage needs from their mentioned usage patterns
     - Connectivity needs from their mentioned devices/peripherals
   
   - Performance priorities based on their most emphasized needs during conversation

5. Always ask the user for budget at least once. if the user refuses or doesnt bother to specify dont pry. estimate it yourself to the precise extint.

6. Keep the conversation flowing naturally for 5-10 exchanges before formulating your recommendation.

7. After you feel you understand their needs, say "I think I have a good understanding of your requirements now. Let me build a custom PC for you." Then invisibly and without showing the user, map their requirements to this JSON format:

\`\`\`json
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
    "marketSegment": "Consumer",
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
\`\`\`

IMPORTANT GUIDELINES FOR CONVERSATION:
- Never show the JSON to the user. When you're ready to generate the recommendation, say "I think I have a good understanding of your requirements now. Let me build a custom PC for you." and then output the JSON between special markers like this: <JSON_START>{ your actual JSON here }</JSON_START>
- Make sure to use the correct closing tag </JSON_START> (not <JSON_END>)
- The <JSON_START> markers should not be visible to the user, they will be processed automatically.
- Be conversational and friendly - never ask for ratings on a scale
- Infer technical requirements from casual conversation
- Be knowledgeable about modern games, applications, and their hardware requirements
- If a user mentions a specific application or game, use your knowledge to infer the appropriate system requirements
- If they say "I want to play Red Dead Redemption 2", understand this means high gaming requirements without asking them to rate it
- If they mention budget constraints, respect them in your assessment
- If they don't mention a use case, assume the intensity is 0
- For marketSegment, set to "Consumer" for typical users who mention gaming, web browsing, general use. Set to "Workstation" if they mention professional workloads like CAD, video production, 3D rendering, scientific computing, or data analysis
- After sufficient conversation, DO NOT display the JSON but output it with the special markers.

Remember to keep your questions conversational and natural. Once you've gathered enough information, say "I think I have a good understanding of your requirements now. Let me build a custom PC for you." and then output the JSON with the special markers.`;

// Define types for the user preferences structure
interface UserPreferencesJson {
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
    cpuPlatform?: string;
    gpuPlatform?: string;
    marketSegment: string;
    formFactor?: string;
    rgbImportance?: number;
    noiseLevel?: string;
    upgradePathImportance?: number;
    storage: {
      ssdCapacity?: string;
      hddCapacity?: string;
    };
    connectivity: {
      wifi?: boolean;
      bluetooth?: boolean;
      usbPorts?: string;
    };
  };
  performancePriorities: {
    cpu?: number;
    gpu?: number;
    ram?: number;
    storageSpeed?: number;
  };
}

// Define the screen states
type Screen = "chat" | "loading" | "results";

const RecommendationBuilder = () => {
  const [messages, setMessages] = useState<
    { role: "user" | "assistant" | "system"; content: string }[]
  >([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [pcBuild, setPcBuild] = useState<BuildRecommendation | null>(null);
  const [screen, setScreen] = useState<Screen>("chat");
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
  }, [messages]);

  // Function to extract JSON from a message
  const extractJson = (message: string) => {
    // Try with proper XML-style closing tag
    const jsonRegex = /<JSON_START>([\s\S]*?)<\/JSON_START>/;
    const match = message.match(jsonRegex);
    if (match && match[1]) {
      try {
        return JSON.parse(match[1]);
      } catch (e) {
        console.error("Failed to parse JSON with </JSON_START> tag:", e);
      }
    }

    // Try with alternate closing tag <JSON_END>
    const altJsonRegex = /<JSON_START>([\s\S]*?)<JSON_END>/;
    const altMatch = message.match(altJsonRegex);
    if (altMatch && altMatch[1]) {
      try {
        return JSON.parse(altMatch[1]);
      } catch (e) {
        console.error("Failed to parse JSON with <JSON_END> tag:", e);
      }
    }

    // Fallback to the code block format
    const oldJsonRegex = /```json\s*([\s\S]*?)\s*```/;
    const oldMatch = message.match(oldJsonRegex);
    if (oldMatch && oldMatch[1]) {
      try {
        return JSON.parse(oldMatch[1]);
      } catch (e) {
        console.error("Failed to parse JSON from code block:", e);
      }
    }

    // Add support for finding JSON without markers (emergency fallback)
    try {
      const jsonPattern =
        /(\{[\s\S]*"budget"[\s\S]*"useCases"[\s\S]*"technicalPreferences"[\s\S]*\})/;
      const rawMatch = message.match(jsonPattern);
      if (rawMatch && rawMatch[1]) {
        return JSON.parse(rawMatch[1]);
      }
    } catch (e) {
      console.error("Failed to parse raw JSON pattern:", e);
    }

    return null;
  };

  // Process the response to remove the JSON if present
  const processResponseAndExtractJson = (fullResponse: string) => {
    const jsonData = extractJson(fullResponse);
    let cleanedResponse = fullResponse;

    if (jsonData) {
      // Remove all possible JSON formats from the displayed message
      cleanedResponse = fullResponse
        .replace(/<JSON_START>[\s\S]*?<\/JSON_START>/, "")
        .replace(/<JSON_START>[\s\S]*?<JSON_END>/, "")
        .replace(/```json[\s\S]*?```/, "")
        .trim();

      // If the response indicates a build is coming, modify it to show a nicer message
      if (cleanedResponse.includes("Let me build a custom PC for you")) {
        cleanedResponse =
          "I think I have a good understanding of your requirements now. Let me build a custom PC for you.";
      }
    }

    return { jsonData, cleanedResponse };
  };

  // Function to send preferences to recommendation system
  const sendToRecommendationSystem = async (
    preferences: UserPreferencesJson
  ) => {
    try {
      // Show loading screen
      setScreen("loading");

      // Create temporary file with preferences
      const response = await axios.post("/api/recommendation", { preferences });

      // Update state with recommendation result
      setPcBuild(response.data);

      // Show results screen
      setScreen("results");
    } catch (error) {
      console.error("Error sending to recommendation system:", error);
      // Return to chat with error message
      setScreen("chat");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I encountered an error while processing your PC build recommendation. Please try again.",
        },
      ]);
    }
  };

  // Function to restart the process
  const handleRestart = () => {
    // Reset states
    setScreen("chat");
    setPcBuild(null);
    setMessages([{ role: "system", content: recommendationSystemPrompt }]);
    setInput("");
  };

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

      // Process the response to remove the JSON if present
      const { jsonData, cleanedResponse } =
        processResponseAndExtractJson(fullResponse);

      // Save the assistant's cleaned message
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: cleanedResponse },
      ]);

      // Process JSON if found and initiate build
      if (
        jsonData &&
        jsonData.budget &&
        jsonData.useCases &&
        jsonData.technicalPreferences
      ) {
        console.log("Found valid JSON configuration:", jsonData);

        // Don't add an extra message, just start processing
        await sendToRecommendationSystem(jsonData);
      }
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

  // Render different screens based on the current state
  if (screen === "loading") {
    return <LoadingScreen />;
  }

  if (screen === "results" && pcBuild) {
    return <BuildResultDisplay pcBuild={pcBuild} onRestart={handleRestart} />;
  }

  // Chat UI
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
    </div>
  );
};

export default RecommendationBuilder;
