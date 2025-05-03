"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { useRouter } from "next/navigation"
import { X } from "lucide-react"

interface CreateProjectModalProps {
  trigger: React.ReactNode
}

export default function CreateProjectModal({ trigger }: CreateProjectModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [repoInput, setRepoInput] = useState("")
  const [error, setError] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const modalRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  useEffect(() => {
    if (!isOpen) return

    // Focus the input when modal opens
    setTimeout(() => {
      inputRef.current?.focus()
    }, 100)

    // Handle escape key
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        closeModal()
      }
    }

    // Handle click outside
    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        closeModal()
      }
    }

    document.addEventListener("keydown", handleKeyDown)
    document.addEventListener("mousedown", handleClickOutside)

    return () => {
      document.removeEventListener("keydown", handleKeyDown)
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [isOpen])

  const openModal = () => {
    setIsOpen(true)
    document.body.style.overflow = "hidden" // Prevent scrolling when modal is open
  }

  const closeModal = () => {
    setIsOpen(false)
    setRepoInput("")
    setError("")
    document.body.style.overflow = "" // Re-enable scrolling
  }

  const validateRepo = (value: string): boolean => {
    // Validate short form: user_name/repo_name
    const shortFormRegex = /^[a-zA-Z0-9_-]+\/[a-zA-Z0-9_.-]+$/

    // Validate full URL: https://github.com/user_name/repo_name
    const fullUrlRegex = /^https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_.-]+\/?$/

    return shortFormRegex.test(value) || fullUrlRegex.test(value)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!repoInput.trim()) {
      setError("Please enter a repository")
      return
    }

    if (!validateRepo(repoInput)) {
      setError(
        "Please enter a valid repository in the format 'user_name/repo_name' or 'https://github.com/user_name/repo_name'",
      )
      return
    }

    setIsSubmitting(true)

    // Mock API call delay
    setTimeout(() => {
      // For now, just redirect to a mock project page
      closeModal()
      router.push("/projects/1")
    }, 800)
  }

  return (
    <>
      <div onClick={openModal} className="cursor-pointer">
        {trigger}
      </div>

      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fadeIn"
          aria-modal="true"
          role="dialog"
        >
          <div
            ref={modalRef}
            className="bg-[#1a1a1a] rounded-lg w-full max-w-md mx-4 shadow-xl border border-[#2a2a2a] animate-scaleIn"
          >
            <div className="flex justify-between items-center p-4 border-b border-[#2a2a2a]">
              <h2 className="text-lg font-semibold text-white">Create New Project</h2>
              <button
                onClick={closeModal}
                className="text-[#a0a0a0] hover:text-white transition-colors p-1 rounded-md hover:bg-[#2a2a2a]"
                aria-label="Close modal"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6">
              <div className="mb-6">
                <label htmlFor="repo-input" className="block mb-2 text-sm font-medium text-white">
                  GitHub Repository
                </label>
                <input
                  ref={inputRef}
                  id="repo-input"
                  type="text"
                  value={repoInput}
                  onChange={(e) => {
                    setRepoInput(e.target.value)
                    setError("")
                  }}
                  placeholder="user_name/repo_name or https://github.com/user_name/repo_name"
                  className="w-full p-3 bg-[#121212] border border-[#333] rounded-md text-white placeholder-[#666] focus:outline-none focus:ring-1 focus:ring-[#ffd700]"
                  aria-describedby="repo-input-error"
                />
                {error && (
                  <p id="repo-input-error" className="mt-2 text-sm text-red-500">
                    {error}
                  </p>
                )}
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 mr-2 text-[#a0a0a0] hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-[#ffd700] text-black font-medium rounded-md hover:bg-[#e6c200] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {isSubmitting ? (
                    <>
                      <svg
                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-black"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Processing...
                    </>
                  ) : (
                    "Let's Go"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
