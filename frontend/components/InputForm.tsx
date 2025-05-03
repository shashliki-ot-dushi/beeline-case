import React from 'react'

interface InputFormProps {
  input: string
  onChange: (val: string) => void
  onSubmit: (e: React.FormEvent) => void
  isLoading: boolean
}

export function InputForm({ input, onChange, onSubmit, isLoading }: InputFormProps) {
  return (
    <div className="p-6 border-t border-[#2a2a2a]">
      <form onSubmit={onSubmit}>
        <textarea
          className="w-full bg-[#1a1a1a] border border-[#333] rounded-xl p-4 text-white resize-none min-h-[60px] outline-none"
          value={input}
          onChange={e => onChange(e.target.value)}
          placeholder="Спросите меня про репозиторий..."
          rows={1}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              onSubmit(e)
            }
          }}
        />
        <button
          type="submit"
          className="absolute bottom-10 right-10 text-[#666] hover:text-[#ffd700] disabled:opacity-50 p-1"
          disabled={isLoading || !input.trim()}
        >
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
          {/* Тут можно разместить иконки спиннера или отправки */}
        </button>
      </form>
    </div>
  )
}
