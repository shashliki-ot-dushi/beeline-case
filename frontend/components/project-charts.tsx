"use client"

import { useState } from "react"
import { BarChart2, LineChart, PieChart } from "lucide-react"

export default function ProjectCharts() {
  const [activeChart, setActiveChart] = useState<"overview" | "performance" | "dependencies">("overview")

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white mb-4">Project Analytics</h2>
          <p className="text-[#a0a0a0] mb-6">
            Visualize your project's code metrics, performance data, and dependency relationships.
          </p>

          <div className="flex space-x-2 mb-6">
            <button
              onClick={() => setActiveChart("overview")}
              className={`px-4 py-2 rounded-md flex items-center gap-2 ${
                activeChart === "overview"
                  ? "bg-[#2a2a2a] text-white"
                  : "text-[#a0a0a0] hover:bg-[#1a1a1a] hover:text-white"
              }`}
            >
              <BarChart2 className="h-4 w-4" />
              <span>Code Overview</span>
            </button>
            <button
              onClick={() => setActiveChart("performance")}
              className={`px-4 py-2 rounded-md flex items-center gap-2 ${
                activeChart === "performance"
                  ? "bg-[#2a2a2a] text-white"
                  : "text-[#a0a0a0] hover:bg-[#1a1a1a] hover:text-white"
              }`}
            >
              <LineChart className="h-4 w-4" />
              <span>Performance</span>
            </button>
            <button
              onClick={() => setActiveChart("dependencies")}
              className={`px-4 py-2 rounded-md flex items-center gap-2 ${
                activeChart === "dependencies"
                  ? "bg-[#2a2a2a] text-white"
                  : "text-[#a0a0a0] hover:bg-[#1a1a1a] hover:text-white"
              }`}
            >
              <PieChart className="h-4 w-4" />
              <span>Dependencies</span>
            </button>
          </div>
        </div>

        {activeChart === "overview" && (
          <div className="space-y-6 animate-fadeIn">
            <div className="bg-[#1a1a1a] rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-medium mb-4 text-white">Code Composition</h3>
              <div className="h-64 flex items-center justify-center">
                <svg width="400" height="200" viewBox="0 0 400 200">
                  <rect width="400" height="200" fill="#1e1e1e" rx="5" />

                  {/* Bar chart */}
                  <rect x="50" y="30" width="60" height="140" fill="#ffd700" opacity="0.8" />
                  <rect x="130" y="70" width="60" height="100" fill="#ffd700" opacity="0.6" />
                  <rect x="210" y="90" width="60" height="80" fill="#ffd700" opacity="0.4" />
                  <rect x="290" y="110" width="60" height="60" fill="#ffd700" opacity="0.2" />

                  {/* Labels */}
                  <text x="80" y="180" textAnchor="middle" fill="white" fontSize="12">
                    JavaScript
                  </text>
                  <text x="160" y="180" textAnchor="middle" fill="white" fontSize="12">
                    TypeScript
                  </text>
                  <text x="240" y="180" textAnchor="middle" fill="white" fontSize="12">
                    CSS
                  </text>
                  <text x="320" y="180" textAnchor="middle" fill="white" fontSize="12">
                    HTML
                  </text>
                </svg>
              </div>
              <div className="grid grid-cols-4 gap-4 mt-4">
                <div className="text-center">
                  <div className="text-lg font-semibold text-white">45%</div>
                  <div className="text-xs text-[#a0a0a0]">JavaScript</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-white">30%</div>
                  <div className="text-xs text-[#a0a0a0]">TypeScript</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-white">15%</div>
                  <div className="text-xs text-[#a0a0a0]">CSS</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-white">10%</div>
                  <div className="text-xs text-[#a0a0a0]">HTML</div>
                </div>
              </div>
            </div>

            <div className="bg-[#1a1a1a] rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-medium mb-4 text-white">Code Complexity</h3>
              <div className="h-64 flex items-center justify-center">
                <svg width="400" height="200" viewBox="0 0 400 200">
                  <rect width="400" height="200" fill="#1e1e1e" rx="5" />

                  {/* Line chart */}
                  <polyline
                    points="50,150 100,120 150,140 200,90 250,110 300,70 350,50"
                    fill="none"
                    stroke="#ffd700"
                    strokeWidth="2"
                  />

                  {/* Dots */}
                  <circle cx="50" cy="150" r="4" fill="#ffd700" />
                  <circle cx="100" cy="120" r="4" fill="#ffd700" />
                  <circle cx="150" cy="140" r="4" fill="#ffd700" />
                  <circle cx="200" cy="90" r="4" fill="#ffd700" />
                  <circle cx="250" cy="110" r="4" fill="#ffd700" />
                  <circle cx="300" cy="70" r="4" fill="#ffd700" />
                  <circle cx="350" cy="50" r="4" fill="#ffd700" />

                  {/* Grid lines */}
                  <line x1="50" y1="30" x2="50" y2="170" stroke="#333" strokeWidth="1" />
                  <line x1="30" y1="170" x2="370" y2="170" stroke="#333" strokeWidth="1" />
                </svg>
              </div>
              <div className="text-center mt-4">
                <div className="text-lg font-semibold text-white">Average Complexity: Medium</div>
                <div className="text-xs text-[#a0a0a0]">Trending upward in recent commits</div>
              </div>
            </div>
          </div>
        )}

        {activeChart === "performance" && (
          <div className="space-y-6 animate-fadeIn">
            <div className="bg-[#1a1a1a] rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-medium mb-4 text-white">Load Time Analysis</h3>
              <div className="h-64 flex items-center justify-center">
                <svg width="400" height="200" viewBox="0 0 400 200">
                  <rect width="400" height="200" fill="#1e1e1e" rx="5" />

                  {/* Area chart */}
                  <path
                    d="M50,170 L50,120 L100,100 L150,130 L200,80 L250,90 L300,70 L350,60 L350,170 Z"
                    fill="#ffd700"
                    opacity="0.2"
                  />
                  <polyline
                    points="50,120 100,100 150,130 200,80 250,90 300,70 350,60"
                    fill="none"
                    stroke="#ffd700"
                    strokeWidth="2"
                  />

                  {/* Grid lines */}
                  <line x1="50" y1="30" x2="50" y2="170" stroke="#333" strokeWidth="1" />
                  <line x1="30" y1="170" x2="370" y2="170" stroke="#333" strokeWidth="1" />
                </svg>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className="text-center">
                  <div className="text-lg font-semibold text-white">1.2s</div>
                  <div className="text-xs text-[#a0a0a0]">Average Load Time</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-white">3.5s</div>
                  <div className="text-xs text-[#a0a0a0]">Slowest Page</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-white">0.8s</div>
                  <div className="text-xs text-[#a0a0a0]">Fastest Page</div>
                </div>
              </div>
            </div>

            <div className="bg-[#1a1a1a] rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-medium mb-4 text-white">Resource Usage</h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <div className="h-40 flex items-center justify-center">
                    <svg width="150" height="150" viewBox="0 0 150 150">
                      <circle cx="75" cy="75" r="60" fill="none" stroke="#333" strokeWidth="10" />
                      <circle
                        cx="75"
                        cy="75"
                        r="60"
                        fill="none"
                        stroke="#ffd700"
                        strokeWidth="10"
                        strokeDasharray="377"
                        strokeDashoffset="94"
                      />
                      <text x="75" y="75" textAnchor="middle" dominantBaseline="middle" fill="white" fontSize="24">
                        75%
                      </text>
                    </svg>
                  </div>
                  <div className="text-center mt-2">
                    <div className="text-sm font-medium text-white">CPU Usage</div>
                  </div>
                </div>
                <div>
                  <div className="h-40 flex items-center justify-center">
                    <svg width="150" height="150" viewBox="0 0 150 150">
                      <circle cx="75" cy="75" r="60" fill="none" stroke="#333" strokeWidth="10" />
                      <circle
                        cx="75"
                        cy="75"
                        r="60"
                        fill="none"
                        stroke="#ffd700"
                        strokeWidth="10"
                        strokeDasharray="377"
                        strokeDashoffset="188"
                      />
                      <text x="75" y="75" textAnchor="middle" dominantBaseline="middle" fill="white" fontSize="24">
                        50%
                      </text>
                    </svg>
                  </div>
                  <div className="text-center mt-2">
                    <div className="text-sm font-medium text-white">Memory Usage</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeChart === "dependencies" && (
          <div className="space-y-6 animate-fadeIn">
            <div className="bg-[#1a1a1a] rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-medium mb-4 text-white">Dependency Graph</h3>
              <div className="h-96 flex items-center justify-center">
                <svg width="500" height="300" viewBox="0 0 500 300">
                  <rect width="500" height="300" fill="#1e1e1e" rx="5" />

                  {/* Main node */}
                  <circle cx="250" cy="150" r="30" fill="#ffd700" opacity="0.8" />
                  <text
                    x="250"
                    y="150"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill="black"
                    fontSize="12"
                    fontWeight="bold"
                  >
                    App
                  </text>

                  {/* Dependency nodes */}
                  <circle cx="150" cy="80" r="20" fill="#ffd700" opacity="0.6" />
                  <text x="150" y="80" textAnchor="middle" dominantBaseline="middle" fill="black" fontSize="10">
                    React
                  </text>

                  <circle cx="350" cy="80" r="20" fill="#ffd700" opacity="0.6" />
                  <text x="350" y="80" textAnchor="middle" dominantBaseline="middle" fill="black" fontSize="10">
                    Next.js
                  </text>

                  <circle cx="100" cy="180" r="15" fill="#ffd700" opacity="0.4" />
                  <text x="100" y="180" textAnchor="middle" dominantBaseline="middle" fill="black" fontSize="8">
                    Redux
                  </text>

                  <circle cx="180" cy="220" r="15" fill="#ffd700" opacity="0.4" />
                  <text x="180" y="220" textAnchor="middle" dominantBaseline="middle" fill="black" fontSize="8">
                    Tailwind
                  </text>

                  <circle cx="320" cy="220" r="15" fill="#ffd700" opacity="0.4" />
                  <text x="320" y="220" textAnchor="middle" dominantBaseline="middle" fill="black" fontSize="8">
                    Axios
                  </text>

                  <circle cx="400" cy="180" r="15" fill="#ffd700" opacity="0.4" />
                  <text x="400" y="180" textAnchor="middle" dominantBaseline="middle" fill="black" fontSize="8">
                    Zod
                  </text>

                  {/* Connection lines */}
                  <line x1="250" y1="150" x2="150" y2="80" stroke="#ffd700" strokeWidth="2" opacity="0.6" />
                  <line x1="250" y1="150" x2="350" y2="80" stroke="#ffd700" strokeWidth="2" opacity="0.6" />
                  <line x1="150" y1="80" x2="100" y2="180" stroke="#ffd700" strokeWidth="1" opacity="0.4" />
                  <line x1="150" y1="80" x2="180" y2="220" stroke="#ffd700" strokeWidth="1" opacity="0.4" />
                  <line x1="350" y1="80" x2="320" y2="220" stroke="#ffd700" strokeWidth="1" opacity="0.4" />
                  <line x1="350" y1="80" x2="400" y2="180" stroke="#ffd700" strokeWidth="1" opacity="0.4" />
                </svg>
              </div>
            </div>

            <div className="bg-[#1a1a1a] rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-medium mb-4 text-white">Dependency Health</h3>
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-[#121212] p-4 rounded-md">
                  <h4 className="text-sm font-medium text-white mb-2">Outdated Packages</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-[#a0a0a0]">react</span>
                      <span className="text-xs text-[#ffd700]">v17.0.2 → v18.2.0</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-[#a0a0a0]">next</span>
                      <span className="text-xs text-[#ffd700]">v12.3.1 → v14.0.4</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-[#a0a0a0]">tailwindcss</span>
                      <span className="text-xs text-[#ffd700]">v3.1.8 → v3.3.0</span>
                    </div>
                  </div>
                </div>
                <div className="bg-[#121212] p-4 rounded-md">
                  <h4 className="text-sm font-medium text-white mb-2">Security Vulnerabilities</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-[#a0a0a0]">High</span>
                      <span className="text-xs text-red-500">2 issues</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-[#a0a0a0]">Medium</span>
                      <span className="text-xs text-yellow-500">5 issues</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-[#a0a0a0]">Low</span>
                      <span className="text-xs text-green-500">3 issues</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
