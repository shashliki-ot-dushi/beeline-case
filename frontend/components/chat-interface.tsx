'use client'

import React, { useState } from 'react'
import { MessageList } from './MessageList'
import { InputForm } from './InputForm'
import { CodePanel } from './CodePanel'
import { Message } from '../types'

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [codePanel, setCodePanel] = useState({ isOpen: false, width: 500, title: '', code: '' })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    setTimeout(() => {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateResponse(input),
      }
      setMessages(prev => [...prev, aiMsg])
      setIsLoading(false)
    }, 1000)
  }

  const generateResponse = (text: string) => {
    // Логика генерации ответа (копирует прежнюю)
    return `AI response for: ${text}`
  }

  const openCodePanel = (code: string, lang: string, title: string) => {
    setCodePanel({ isOpen: true, width: codePanel.width, title, code })
  }

  const closeCodePanel = () => setCodePanel(prev => ({ ...prev, isOpen: false }))

  const startResize = (e: React.MouseEvent) => {
    const startW = codePanel.width
    const startX = e.pageX
    const onMove = (ev: MouseEvent) => {
      const nw = startW - (ev.pageX - startX)
      if (nw > 300 && nw < window.innerWidth * 0.8) setCodePanel(prev => ({ ...prev, width: nw }))
    }
    const onUp = () => {
      document.body.removeEventListener('mousemove', onMove)
      document.body.removeEventListener('mouseup', onUp)
    }
    document.body.addEventListener('mousemove', onMove)
    document.body.addEventListener('mouseup', onUp)
  }

  const handleDiagramClick = () => {
    // Открыть панель с кодом диаграммы
    openCodePanel(
      `// React code для lifecycle...`,
      'jsx',
      'Component Lifecycle Implementation',
    )
  }

  return (
    <div className="flex flex-col h-full relative">
      <MessageList messages={messages} onViewCode={openCodePanel} onDiagramClick={handleDiagramClick} />
      <InputForm
        input={input}
        onChange={setInput}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />
      <CodePanel
        isOpen={codePanel.isOpen}
        width={codePanel.width}
        title={codePanel.title}
        code={codePanel.code}
        onClose={closeCodePanel}
        onStartResize={startResize}
      />
    </div>
  )
}