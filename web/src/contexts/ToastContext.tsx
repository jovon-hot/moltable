'use client'

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react'

type ToastType = 'success' | 'error' | 'info'

interface Toast {
  id: number
  message: string
  type: ToastType
}

interface ToastContextType {
  toast: (message: string, type?: ToastType) => void
}

const ToastContext = createContext<ToastContextType>({ toast: () => {} })

export function useToast() {
  return useContext(ToastContext)
}

let toastId = 0

const iconMap: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle size={16} style={{ color: '#4338CA' }} />,
  error: <AlertCircle size={16} style={{ color: '#f87171' }} />,
  info: <Info size={16} style={{ color: '#d0d6e0' }} />,
}

const borderColorMap: Record<ToastType, string> = {
  success: '#4338CA',
  error: '#f87171',
  info: '#d0d6e0',
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = ++toastId
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 4000)
  }, [])

  const removeToast = (id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 max-w-sm">
        {toasts.map(t => (
          <div
            key={t.id}
            role="alert"
            aria-live="polite"
            className="flex items-start gap-3 px-4 py-3 rounded-lg transition-all duration-300 animate-in slide-in-from-right"
            style={{
              background: '#191a1b',
              boxShadow: `0 0 0 1px rgba(255,255,255,0.08), inset 0 0 0 3px ${borderColorMap[t.type]}`,
            }}
          >
            <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center mt-0.5">
              {iconMap[t.type]}
            </span>
            <p className="text-sm flex-1" style={{ color: '#ffffff' }}>{t.message}</p>
            <button
              onClick={() => removeToast(t.id)}
              className="flex-shrink-0 transition-colors"
              style={{ color: '#888888' }}
              onMouseEnter={e => e.currentTarget.style.color = '#ffffff'}
              onMouseLeave={e => e.currentTarget.style.color = '#888888'}
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
