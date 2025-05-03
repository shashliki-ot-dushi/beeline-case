import { openai } from "@ai-sdk/openai"
import { streamText, tool } from "ai"
import { z } from "zod"

export async function POST(req: Request) {
  const { messages } = await req.json()

  const result = streamText({
    model: openai("gpt-4o"),
    system: `You are CodeAI, an advanced code analysis assistant. 
    You help developers understand, optimize, and debug their code.
    When analyzing code:
    1. Identify potential bugs and issues
    2. Suggest optimizations and improvements
    3. Explain complex code sections
    4. Provide best practices and patterns
    Always format code examples using markdown code blocks with the appropriate language.`,
    messages,
    tools: {
      analyzeCode: tool({
        description: "Analyze code for bugs, optimizations, and best practices",
        parameters: z.object({
          code: z.string().describe("The code to analyze"),
          language: z.string().describe("The programming language of the code"),
        }),
        execute: async ({ code, language }) => {
          // In a real application, this would connect to a more sophisticated
          // code analysis service or use RAG to retrieve relevant information
          return {
            analysis: `Analysis for ${language} code:
1. Code structure is well-organized
2. Consider adding more comments for better readability
3. There might be potential performance improvements`,
            suggestions: [
              "Add comprehensive error handling",
              "Consider breaking down complex functions",
              "Add unit tests for critical functionality",
            ],
          }
        },
      }),
      searchDocs: tool({
        description: "Search documentation and knowledge base for programming concepts",
        parameters: z.object({
          query: z.string().describe("The search query"),
          language: z.string().optional().describe("The programming language to focus on"),
        }),
        execute: async ({ query, language }) => {
          // In a real application, this would connect to a vector database
          // with programming documentation and knowledge
          return {
            results: [
              {
                title: `${language || "Programming"} best practices for ${query}`,
                content: `Here are some best practices related to your query...`,
              },
              {
                title: `Common patterns for ${query}`,
                content: `Developers often use these patterns...`,
              },
            ],
          }
        },
      }),
    },
  })

  return result.toDataStreamResponse()
}
