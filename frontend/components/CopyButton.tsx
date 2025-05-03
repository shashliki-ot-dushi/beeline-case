import React, { useState } from 'react'
import { Copy, Check } from 'lucide-react'

interface CopyButtonProps {
  code: string
}

export function CopyButton({ code }: CopyButtonProps) {
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