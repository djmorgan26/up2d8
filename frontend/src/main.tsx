import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const rootElement = document.getElementById('root')
console.log('Root element found:', rootElement)

if (!rootElement) {
  console.error('Failed to find root element')
  const body = document.body
  const div = document.createElement('div')
  div.id = 'root'
  body.appendChild(div)
}

try {
  console.log('Starting React application...')
  createRoot(rootElement ?? document.getElementById('root')!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
  console.log('React application mounted successfully')
} catch (error) {
  console.error('Failed to mount React application:', error)
  document.body.innerHTML = '<div style="color: red; padding: 20px;">Failed to load application. Check console for details.</div>'
}
