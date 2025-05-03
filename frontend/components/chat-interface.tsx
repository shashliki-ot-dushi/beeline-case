"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { ChevronRight, Copy, Check } from "lucide-react"

export default function ChatInterface() {
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [codePanel, setCodePanel] = useState<{
    isOpen: boolean
    code: string
    language: string
    title: string
  }>({
    isOpen: false,
    code: "",
    language: "",
    title: "",
  })
  const [codePanelWidth, setCodePanelWidth] = useState(500)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: generateResponse(input),
      }
      setMessages((prev) => [...prev, aiMessage])
      setIsLoading(false)
    }, 1000)
  }

  const generateResponse = (userInput: string) => {
    if (userInput.toLowerCase().includes("javascript")) {
      return `Here's an example of modern JavaScript code:

\`\`\`javascript
// Async/await example
async function fetchUserData(userId) {
  try {
    const response = await fetch(\`https://api.example.com/users/\${userId}\`);
    if (!response.ok) {
      throw new Error('Failed to fetch user data');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    return null;
  }
}
\`\`\`

This pattern uses async/await for cleaner asynchronous code handling.`
    }

    if (userInput.toLowerCase().includes("diagram") || userInput.toLowerCase().includes("flow")) {
      return `Here's a diagram showing the component lifecycle:

\`\`\`mermaid
graph TD
    A["Component Created"] --> B["Mount Phase"]
    B --> C["Update Phase"]
    C --> D["Unmount Phase"]
    C --> B
\`\`\`

Click on the diagram to see the implementation code.`
    }

    return `Я могу помочь вам проанализировать ваш код.`
  }

  const openCodePanel = (code: string, language: string, title: string) => {
    setCodePanel({
      isOpen: true,
      code,
      language,
      title,
    })
  }

  const closeCodePanel = () => {
    setCodePanel((prev) => ({ ...prev, isOpen: false }))
  }

  const handleDiagramClick = () => {
    openCodePanel(
      `import React, { useEffect, useState } from 'react';

function ComponentLifecycle() {
  // Mount phase
  const [data, setData] = useState(null);
  
  // Update phase
  useEffect(() => {
    // Fetch data when component mounts
    fetchData();
    
    // Unmount phase
    return () => {
      // Clean up resources
      console.log('Component unmounting');
    };
  }, []);
  
  const fetchData = async () => {
    const result = await fetch('/api/data');
    const json = await result.json();
    setData(json);
  };
  
  return (
    <div>
      {data ? <DisplayData data={data} /> : <Loading />}
    </div>
  );
}`,
      "jsx",
      "Component Lifecycle Implementation",
    )
  }

  const startResizing = (mouseDownEvent: React.MouseEvent) => {
    const startWidth = codePanelWidth
    const startPosition = mouseDownEvent.pageX

    // Add CSS to prevent text selection during resize
    document.body.style.userSelect = 'none'
    document.body.style.webkitUserSelect = 'none'

    function onMouseMove(mouseMoveEvent: MouseEvent) {
      const newWidth = startWidth - (mouseMoveEvent.pageX - startPosition)
      if (newWidth > 300 && newWidth < window.innerWidth * 0.8) {
        setCodePanelWidth(newWidth)
      }
    }

    function onMouseUp() {
      // Restore text selection
      document.body.style.userSelect = ''
      document.body.style.webkitUserSelect = ''
      document.body.removeEventListener("mousemove", onMouseMove)
      document.body.removeEventListener("mouseup", onMouseUp)
    }

    document.body.addEventListener("mousemove", onMouseMove)
    document.body.addEventListener("mouseup", onMouseUp)
  }

  return (
    <div className="flex flex-col h-full relative">
      <div className={`flex-1 overflow-y-auto p-4 ${codePanel.isOpen ? "mr-[" + codePanelWidth + "px]" : ""}`}>
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="relative">
              <div className="absolute w-[300px] h-[300px] bg-[#ffd700] opacity-10 rounded-full blur-3xl -top-[150px] -left-[150px]"></div>
                <img src="https://static.beeline.ru/upload/dpcupload/contents/342/avatarbee_2704.svg" className="transform scale-[2] mb-20"></img>
            </div>
            <h2 className="text-2xl font-bold mb-2 text-white">ИИ анализ кода</h2>
            <p className="text-[#a0a0a0] max-w-md mb-8">
            Загрузите свой код, чтобы получить анализ на основе искусственного интеллекта.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`mb-6 ${message.role === "user" ? "flex justify-end" : "flex justify-start"}`}
            >
              <div
                className={`max-w-3xl rounded-2xl px-4 py-3 ${
                  message.role === "user" ? "bg-[#ffd700] text-black" : "bg-[#1a1a1a] text-white"
                }`}
                style={{ maxWidth: "80%" }}
              >
                {message.content.includes("```mermaid") ? (
                  <div>
                    {message.content.split("```").map((part: string, index: number) => {
                      if (index % 2 === 0) {
                        return (
                          <p key={index} className="whitespace-pre-wrap mb-2">
                            {part}
                          </p>
                        )
                      } else if (part.startsWith("mermaid")) {
                        return (
                          <div
                            key={index}
                            className="my-4 p-4 bg-[#121212] rounded-md cursor-pointer hover:bg-[#1e1e1e] transition-colors"
                            onClick={handleDiagramClick}
                          >
                            <div className="text-center text-[#a0a0a0] text-sm mb-2">Click to view implementation</div>
                            <div className="flex justify-center">
                              <svg width="300" height="200" viewBox="0 0 300 200">
                                <rect width="300" height="200" fill="#1e1e1e" rx="5" />
                                <text x="150" y="40" textAnchor="middle" fill="#ffd700" fontSize="16">
                                  Component Created
                                </text>
                                <line x1="150" y1="45" x2="150" y2="70" stroke="#ffd700" strokeWidth="2" />
                                <text x="150" y="90" textAnchor="middle" fill="#ffd700" fontSize="16">
                                  Mount Phase
                                </text>
                                <line x1="150" y1="95" x2="150" y2="120" stroke="#ffd700" strokeWidth="2" />
                                <text x="150" y="140" textAnchor="middle" fill="#ffd700" fontSize="16">
                                  Update Phase
                                </text>
                                <line x1="150" y1="145" x2="100" y2="170" stroke="#ffd700" strokeWidth="2" />
                                <line x1="150" y1="145" x2="200" y2="170" stroke="#ffd700" strokeWidth="2" />
                                <text x="100" y="190" textAnchor="middle" fill="#ffd700" fontSize="16">
                                  Unmount Phase
                                </text>
                                <path
                                  d="M200,170 C220,150 220,110 150,90"
                                  stroke="#ffd700"
                                  strokeWidth="2"
                                  fill="transparent"
                                />
                              </svg>
                            </div>
                          </div>
                        )
                      } else {
                        const [language, ...code] = part.split("\n")
                        return (
                          <div key={index} className="my-4 rounded-md overflow-hidden">
                            <div className="bg-[#1e1e1e] px-4 py-1.5 text-xs text-[#a0a0a0] flex justify-between items-center">
                              <span>{language}</span>
                              <button
                                className="flex items-center gap-1 hover:text-white transition-colors"
                                onClick={() => openCodePanel(code.join("\n"), language, "Code Example")}
                              >
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="2"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  className="h-3.5 w-3.5"
                                >
                                  <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                                  <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
                                </svg>
                                <span>View code</span>
                              </button>
                            </div>
                            <pre className="p-4 overflow-x-auto bg-[#121212] text-sm">
                              <code>{code.join("\n")}</code>
                            </pre>
                          </div>
                        )
                      }
                    })}
                  </div>
                ) : message.content.includes("```") ? (
                  <div>
                    {message.content.split("```").map((part: string, index: number) => {
                      if (index % 2 === 0) {
                        return (
                          <p key={index} className="whitespace-pre-wrap mb-2">
                            {part}
                          </p>
                        )
                      } else {
                        const [language, ...code] = part.split("\n")
                        return (
                          <div key={index} className="my-4 rounded-md overflow-hidden">
                            <div className="bg-[#1e1e1e] px-4 py-1.5 text-xs text-[#a0a0a0] flex justify-between items-center">
                              <span>{language}</span>
                              <button
                                className="flex items-center gap-1 hover:text-white transition-colors"
                                onClick={() => openCodePanel(code.join("\n"), language, "Code Example")}
                              >
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="2"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  className="h-3.5 w-3.5"
                                >
                                  <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                                  <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
                                </svg>
                                <span>View code</span>
                              </button>
                            </div>
                            <pre className="p-4 overflow-x-auto bg-[#121212] text-sm">
                              <code>{code.join("\n")}</code>
                            </pre>
                          </div>
                        )
                      }
                    })}
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-6 border-t border-[#2a2a2a]">
        <form onSubmit={handleSubmit}>
          <div className="relative">
            <textarea
              className="w-full bg-[#1a1a1a] border border-[#333] rounded-xl p-4 text-white resize-none min-h-[60px] outline-none"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Задайте вопрос"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
            />
            <button
              type="submit"
              className="absolute bottom-4 right-3 text-[#666] hover:text-[#ffd700] disabled:opacity-50 p-1"
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? (
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5"
                >
                  <path d="M22 2L11 13" />
                  <path d="M22 2l-7 20-4-9-9-4 20-7z" />
                </svg>
              )}
            </button>
          </div>
        </form>
      </div>

      {codePanel.isOpen && (
        <div
          className="fixed top-0 right-0 h-full bg-[#121212] border-l border-[#2a2a2a] shadow-xl z-10 flex flex-col"
          style={{ width: `${codePanelWidth}px` }}
        >
          <div
            className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-[#ffd700] select-none"
            onMouseDown={startResizing}
          ></div>
          <div className="flex items-center justify-between p-4 border-b border-[#2a2a2a]">
            <div className="flex items-center">
              <button onClick={closeCodePanel} className="mr-3 hover:bg-[#2a2a2a] p-1 rounded-md">
                <ChevronRight className="h-5 w-5" />
              </button>
              <h3 className="font-medium text-white">{codePanel.title}</h3>
            </div>
            <CopyButton code={codePanel.code} />
          </div>
          <div className="flex-1 overflow-auto p-4">
            <pre className="text-sm">
              <code>{codePanel.code}</code>
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

function CopyButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={copyToClipboard}
      className="flex items-center gap-1 text-[#a0a0a0] hover:text-white transition-colors text-sm"
    >
      {copied ? (
        <>
          <Check className="h-4 w-4" />
          <span>Copied!</span>
        </>
      ) : (
        <>
          <Copy className="h-4 w-4" />
          <span>Copy code</span>
        </>
      )}
    </button>
  )
}
