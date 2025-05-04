"use client"

import { useState } from "react"
import { Download, Search, FileText, Code, BookOpen, Settings } from "lucide-react"

export default function ProjectDocumentation() {
  const [searchQuery, setSearchQuery] = useState("")
  const [activeSection, setActiveSection] = useState<"overview" | "api" | "components" | "setup">("overview")

  return (
    <div className="h-full overflow-hidden flex">
      {/* Sidebar */}
      <div className="w-64 bg-[#1a1a1a] border-r border-[#2a2a2a] p-4 flex flex-col">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#666]" />
            <input
              type="text"
              placeholder="Search documentation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#121212] border border-[#333] rounded-xl py-2 pl-10 pr-4 text-sm text-white placeholder-[#666] focus:outline-none focus:border-[#444]"
            />
          </div>
        </div>

        <nav className="space-y-1">
          <button
            onClick={() => setActiveSection("overview")}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm ${
              activeSection === "overview"
                ? "bg-[#2a2a2a] text-white"
                : "text-[#a0a0a0] hover:bg-[#2a2a2a] hover:text-white"
            }`}
          >
            <BookOpen className="h-4 w-4" />
            <span>Overview</span>
          </button>
          <button
            onClick={() => setActiveSection("api")}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm ${
              activeSection === "api" ? "bg-[#2a2a2a] text-white" : "text-[#a0a0a0] hover:bg-[#2a2a2a] hover:text-white"
            }`}
          >
            <Code className="h-4 w-4" />
            <span>API Reference</span>
          </button>
          <button
            onClick={() => setActiveSection("components")}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm ${
              activeSection === "components"
                ? "bg-[#2a2a2a] text-white"
                : "text-[#a0a0a0] hover:bg-[#2a2a2a] hover:text-white"
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Components</span>
          </button>
          <button
            onClick={() => setActiveSection("setup")}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm ${
              activeSection === "setup"
                ? "bg-[#2a2a2a] text-white"
                : "text-[#a0a0a0] hover:bg-[#2a2a2a] hover:text-white"
            }`}
          >
            <Settings className="h-4 w-4" />
            <span>Setup Guide</span>
          </button>
        </nav>

        <div className="mt-auto pt-4 border-t border-[#2a2a2a]">
          <button className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-[#2a2a2a] hover:bg-[#333] rounded-xl text-sm text-white transition-colors">
            <Download className="h-4 w-4" />
            <span>Download Docs</span>
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-y-auto p-6 bg-gradient-radial">
        <div className="max-w-3xl mx-auto">
          {activeSection === "overview" && (
            <div className="space-y-6 animate-fadeIn">
              <div>
                <h1 className="text-3xl font-bold text-white mb-4">Project Documentation</h1>
                <p className="text-[#a0a0a0] mb-6">
                  This documentation provides an overview of the project structure, API references, and usage
                  guidelines.
                </p>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">Introduction</h2>
                <p className="text-[#a0a0a0] mb-4">
                  This project is a code analysis platform built with Next.js and React. It provides tools for analyzing
                  code quality, performance, and security issues.
                </p>
                <p className="text-[#a0a0a0]">
                  The application uses modern JavaScript practices and follows a component-based architecture for
                  maintainability and scalability.
                </p>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">Key Features</h2>
                <ul className="list-disc pl-5 text-[#a0a0a0] space-y-2">
                  <li>Real-time code analysis with AI-powered suggestions</li>
                  <li>Interactive visualization of code metrics and dependencies</li>
                  <li>Collaborative chat interface for team discussions</li>
                  <li>Comprehensive documentation generation</li>
                  <li>Performance monitoring and optimization recommendations</li>
                </ul>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">Tech Stack</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-lg font-medium text-white mb-2">Frontend</h3>
                    <ul className="list-disc pl-5 text-[#a0a0a0] space-y-1">
                      <li>Next.js</li>
                      <li>React</li>
                      <li>TypeScript</li>
                      <li>Tailwind CSS</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-white mb-2">Backend</h3>
                    <ul className="list-disc pl-5 text-[#a0a0a0] space-y-1">
                      <li>Node.js</li>
                      <li>OpenAI API</li>
                      <li>AI SDK</li>
                      <li>Zod</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === "api" && (
            <div className="space-y-6 animate-fadeIn">
              <div>
                <h1 className="text-3xl font-bold text-white mb-4">API Reference</h1>
                <p className="text-[#a0a0a0] mb-6">
                  Comprehensive documentation of the available API endpoints and their usage.
                </p>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">Authentication</h2>
                <p className="text-[#a0a0a0] mb-4">
                  All API requests require authentication using a bearer token in the Authorization header.
                </p>
                <div className="bg-[#121212] p-4 rounded-xl">
                  <pre className="text-sm text-[#a0a0a0]">
                    <code>{`Authorization: Bearer YOUR_API_TOKEN`}</code>
                  </pre>
                </div>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">Endpoints</h2>

                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-green-900 text-green-300 rounded text-xs font-medium">POST</span>
                    <span className="text-white font-mono text-sm">/api/chat</span>
                  </div>
                  <p className="text-[#a0a0a0] mb-3">Send a message to the AI assistant for code analysis.</p>
                  <div className="bg-[#121212] p-4 rounded-xl mb-3">
                    <pre className="text-sm text-[#a0a0a0]">
                      <code>{`// Request body
{
  "messages": [
    {
      "role": "user",
      "content": "Analyze this React component for performance issues"
    }
  ]
}`}</code>
                    </pre>
                  </div>
                  <div className="bg-[#121212] p-4 rounded-xl">
                    <pre className="text-sm text-[#a0a0a0]">
                      <code>{`// Response
{
  "id": "msg_123",
  "role": "assistant",
  "content": "Here's my analysis of your React component..."
}`}</code>
                    </pre>
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-blue-900 text-blue-300 rounded text-xs font-medium">GET</span>
                    <span className="text-white font-mono text-sm">/api/projects/:id</span>
                  </div>
                  <p className="text-[#a0a0a0] mb-3">Retrieve details about a specific project.</p>
                  <div className="bg-[#121212] p-4 rounded-xl">
                    <pre className="text-sm text-[#a0a0a0]">
                      <code>{`// Response
{
  "id": "proj_123",
  "name": "My Project",
  "repository": "user/repo",
  "created_at": "2023-05-15T10:30:00Z",
  "chats": [
    {
      "id": "chat_1",
      "title": "Performance Analysis"
    }
  ]
}`}</code>
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === "components" && (
            <div className="space-y-6 animate-fadeIn">
              <div>
                <h1 className="text-3xl font-bold text-white mb-4">Components</h1>
                <p className="text-[#a0a0a0] mb-6">
                  Documentation for the key React components used in the application.
                </p>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">ChatInterface</h2>
                <p className="text-[#a0a0a0] mb-4">
                  The main chat interface component that handles user interactions with the AI assistant.
                </p>
                <div className="bg-[#121212] p-4 rounded-xl mb-4">
                  <pre className="text-sm text-[#a0a0a0]">
                    <code>{`import ChatInterface from "@/components/chat-interface"

// Usage
<ChatInterface />`}</code>
                  </pre>
                </div>
                <h3 className="text-lg font-medium text-white mb-2">Props</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-[#a0a0a0] uppercase">
                      <tr>
                        <th className="px-4 py-2">Name</th>
                        <th className="px-4 py-2">Type</th>
                        <th className="px-4 py-2">Default</th>
                        <th className="px-4 py-2">Description</th>
                      </tr>
                    </thead>
                    <tbody className="text-[#a0a0a0]">
                      <tr className="border-b border-[#2a2a2a]">
                        <td className="px-4 py-2">initialMessages</td>
                        <td className="px-4 py-2">Message[]</td>
                        <td className="px-4 py-2">[]</td>
                        <td className="px-4 py-2">Initial messages to display in the chat</td>
                      </tr>
                      <tr className="border-b border-[#2a2a2a]">
                        <td className="px-4 py-2">onSend</td>
                        <td className="px-4 py-2">function</td>
                        <td className="px-4 py-2">undefined</td>
                        <td className="px-4 py-2">Callback function when a message is sent</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">ProjectCharts</h2>
                <p className="text-[#a0a0a0] mb-4">Component for visualizing project metrics and analytics data.</p>
                <div className="bg-[#121212] p-4 rounded-xl mb-4">
                  <pre className="text-sm text-[#a0a0a0]">
                    <code>{`import ProjectCharts from "@/components/project-charts"

// Usage
<ProjectCharts projectId="proj_123" />`}</code>
                  </pre>
                </div>
                <h3 className="text-lg font-medium text-white mb-2">Props</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-[#a0a0a0] uppercase">
                      <tr>
                        <th className="px-4 py-2">Name</th>
                        <th className="px-4 py-2">Type</th>
                        <th className="px-4 py-2">Default</th>
                        <th className="px-4 py-2">Description</th>
                      </tr>
                    </thead>
                    <tbody className="text-[#a0a0a0]">
                      <tr className="border-b border-[#2a2a2a]">
                        <td className="px-4 py-2">projectId</td>
                        <td className="px-4 py-2">string</td>
                        <td className="px-4 py-2">required</td>
                        <td className="px-4 py-2">ID of the project to display charts for</td>
                      </tr>
                      <tr className="border-b border-[#2a2a2a]">
                        <td className="px-4 py-2">timeRange</td>
                        <td className="px-4 py-2">string</td>
                        <td className="px-4 py-2">'week'</td>
                        <td className="px-4 py-2">Time range for the charts (day, week, month)</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeSection === "setup" && (
            <div className="space-y-6 animate-fadeIn">
              <div>
                <h1 className="text-3xl font-bold text-white mb-4">Setup Guide</h1>
                <p className="text-[#a0a0a0] mb-6">
                  Step-by-step instructions for setting up and running the project locally.
                </p>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">Prerequisites</h2>
                <ul className="list-disc pl-5 text-[#a0a0a0] space-y-2">
                  <li>Node.js 18.0 or higher</li>
                  <li>npm or yarn package manager</li>
                  <li>OpenAI API key</li>
                </ul>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">Installation</h2>
                <ol className="list-decimal pl-5 text-[#a0a0a0] space-y-4">
                  <li>
                    <p className="mb-2">Clone the repository</p>
                    <div className="bg-[#121212] p-4 rounded-xl">
                      <pre className="text-sm text-[#a0a0a0]">
                        <code>git clone https://github.com/username/code-analysis-platform.git</code>
                      </pre>
                    </div>
                  </li>
                  <li>
                    <p className="mb-2">Install dependencies</p>
                    <div className="bg-[#121212] p-4 rounded-xl">
                      <pre className="text-sm text-[#a0a0a0]">
                        <code>cd code-analysis-platform npm install</code>
                      </pre>
                    </div>
                  </li>
                  <li>
                    <p className="mb-2">Set up environment variables</p>
                    <p className="mb-2">Create a .env.local file in the root directory with the following variables:</p>
                    <div className="bg-[#121212] p-4 rounded-xl">
                      <pre className="text-sm text-[#a0a0a0]">
                        <code>OPENAI_API_KEY=your_openai_api_key</code>
                      </pre>
                    </div>
                  </li>
                  <li>
                    <p className="mb-2">Start the development server</p>
                    <div className="bg-[#121212] p-4 rounded-xl">
                      <pre className="text-sm text-[#a0a0a0]">
                        <code>npm run dev</code>
                      </pre>
                    </div>
                  </li>
                </ol>
              </div>

              <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-semibold text-white mb-4">Configuration</h2>
                <p className="text-[#a0a0a0] mb-4">
                  Additional configuration options can be set in the config.js file:
                </p>
                <div className="bg-[#121212] p-4 rounded-xl">
                  <pre className="text-sm text-[#a0a0a0]">
                    <code>{`// config.js
module.exports = {
  apiUrl: process.env.API_URL || 'http://localhost:3000/api',
  maxTokens: 4096,
  defaultModel: 'gpt-4o',
  theme: {
    primary: '#ffd700',
    background: '#0f0f0f',
    card: '#1a1a1a',
    border: '#2a2a2a',
  }
}`}</code>
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
