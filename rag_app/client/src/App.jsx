import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, FileText, Loader2, Bot, User } from 'lucide-react';
import './index.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setStatus('Processing document...');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setStatus(`Success: Processed ${data.chunks_processed} chunks`);
    } catch (error) {
      console.error('Upload failed:', error);
      setStatus('Upload failed. Is the server running?');
    } finally {
      setUploading(false);
    }
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });
      const data = await response.json();
      setMessages(prev => [...prev, { 
        text: data.answer, 
        isUser: false,
        sources: data.sources 
      }]);
    } catch (error) {
      console.error('Query failed:', error);
      setMessages(prev => [...prev, { 
        text: 'Sorry, I couldn\'t connect to the AI service. Please make sure the backend is running.', 
        isUser: false 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Endee RAG Assistant</h1>
        <p style={{ color: 'var(--text-muted)' }}>Powered by Gemma3 & Endee Vector DB</p>
      </header>

      <div className="glass-card upload-section">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'rgba(99, 102, 241, 0.2)', padding: '0.5rem', borderRadius: '0.5rem' }}>
            {uploading ? <Loader2 className="animate-spin" color="#818cf8" /> : <FileText color="#818cf8" />}
          </div>
          <div>
            <p style={{ fontWeight: '600' }}>Knowledge Base</p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{status || 'Upload a PDF to get started'}</p>
          </div>
        </div>
        <label className="button-upload">
          <input type="file" onChange={handleFileUpload} accept=".pdf,.txt" style={{ display: 'none' }} />
          <button as="span" style={{ pointerEvents: 'none', background: 'var(--primary)', color: 'white', padding: '0.75rem', borderRadius: '0.5rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Upload size={18} />
            {uploading ? 'Processing...' : 'Upload File'}
          </button>
        </label>
      </div>

      <div className="glass-card chat-window">
        <div className="messages">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '20%', color: 'var(--text-muted)' }}>
              <Bot size={48} style={{ marginBottom: '1rem', opacity: 0.5, margin: '0 auto' }} />
              <p>Hello! Upload a document and ask me anything about it.</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.isUser ? 'user-message' : 'bot-message'}`}>
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.25rem' }}>
                {msg.isUser ? <User size={14} /> : <Bot size={14} />}
                <span style={{ fontSize: '0.7rem', fontWeight: 'bold', textTransform: 'uppercase' }}>
                  {msg.isUser ? 'You' : 'Gemma3'}
                </span>
              </div>
              <div>{msg.text}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources-info">
                  Sources: {msg.sources.length} matching segments found
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message bot-message">
              <Loader2 className="animate-spin" size={20} />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="input-area">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            <Send size={18} />
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
