"use client"

import type React from "react"

import { useState } from "react"
import { ChevronRight, Copy, Check } from "lucide-react"

interface CodePanelProps {
  code: string
  language: string
  title: string
  isOpen: boolean
  onClose: () => void
  width: number
  onResize: (width: number) => void
}

export default function CodePanel({ code, language, title, isOpen, onClose, width, onResize }: CodePanelProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const startResizing = (mouseDownEvent: React.MouseEvent) => {
    const startWidth = width
    const startPosition = mouseDownEvent.pageX

    function onMouseMove(mouseMoveEvent: MouseEvent) {
      const newWidth = startWidth - (mouseMoveEvent.pageX - startPosition)
      if (newWidth > 300 && newWidth < window.innerWidth * 0.8) {
        onResize(newWidth)
      }
    }

    function onMouseUp() {
      document.body.removeEventListener("mousemove", onMouseMove)
      document.body.removeEventListener("mouseup", onMouseUp)
    }

    document.body.addEventListener("mousemove", onMouseMove)
    document.body.addEventListener("mouseup", onMouseUp)
  }

  if (!isOpen) return null

  return (
    <div
      className="fixed top-0 right-0 h-full bg-[#121212] border-l border-[#2a2a2a] shadow-xl z-10 flex flex-col"
      style={{ width: `${width}px` }}
    >
      <div
        className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-[#ffd700]"
        onMouseDown={startResizing}
      ></div>
      <div className="flex items-center justify-between p-4 border-b border-[#2a2a2a]">
        <div className="flex items-center">
          <button onClick={onClose} className="mr-3 hover:bg-[#2a2a2a] p-1 rounded-md">
            <ChevronRight className="h-5 w-5" />
          </button>
          <h3 className="font-medium text-white">{title}</h3>
        </div>
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
      </div>
      <div className="flex-1 overflow-auto p-4">
        <pre className="text-sm">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  )
}
