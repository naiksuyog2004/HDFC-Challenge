import { useState } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Management Radar</h1>
          <p>Management intelligence dashboard</p>
        </div>

        <select>
          <option>Maruti Suzuki</option>
          <option>Infosys</option>
        </select>
      </header>

      <main className="main">
        <section className="hero">
          <h2>Management Intelligence</h2>
          <p>
            Track company announcements, management interviews,
            important topics and AI-powered insights.
          </p>
        </section>

        <section className="content">
          <div className="timeline">
            <h2>Company Timeline</h2>

            <div className="empty-state">
              <h3>No sources processed yet</h3>
              <p>
                Your announcements and management interviews
                will appear here after ingestion.
              </p>
            </div>
          </div>

          <div className="chat">
            <h2>Ask Management Radar</h2>

            <div className="chat-box">
              <p>
                Ask questions about management commentary,
                expansion plans, margins, risks and more.
              </p>

              <div className="input-row">
                <input
                  type="text"
                  placeholder="What has management said about expansion?"
                />

                <button>Ask</button>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
