import React from 'react'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>DIAN Compliance Platform</h1>
        <p>Welcome to the DIAN Compliance Platform Frontend</p>
        <div className="status">
          <h2>Service Status</h2>
          <p>API Gateway: <span className="status-ok">✅ Online</span></p>
          <p>Frontend: <span className="status-ok">✅ Online</span></p>
        </div>
      </header>
    </div>
  )
}

export default App
