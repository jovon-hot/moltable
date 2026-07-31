import { Toaster as RadixToaster } from 'sonner'

export function Toaster() {
  return (
    <RadixToaster
      position="bottom-right"
      toastOptions={{
        classNames: {
          toast: 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700',
          title: 'text-slate-900 dark:text-slate-100',
          description: 'text-slate-500 dark:text-slate-400',
          actionButton: 'bg-primary-600 text-white',
          cancelButton: 'bg-slate-200 text-slate-900',
        },
      }}
    />
  )
}
