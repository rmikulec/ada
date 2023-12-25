// App.js
import React from 'react';
import './App.css';
import Chat from './components/Chat';
import ExplainedDocument from './components/ExplainedDocument';
import ReferenceOverlay from './components/ReferenceOverlay';

import { QuestionProvider } from './services/questionProvider';
import { AppStateProvider } from './services/appProvider';

function App() {
  return (
    <AppStateProvider>
      <QuestionProvider>
        <div className="App">
          <header className="App-header">
            <h1>Ada</h1>
          </header>
          <div id="chat-section" className="container-fluid" style={{ minHeight: '100vh'}}>
            <ReferenceOverlay/>
            <div className="row" style={{ minHeight: '100vh'}}>
              <div className="col-md-4">
              <Chat />
              </div>
              <div className="col-md-8">
                <ExplainedDocument />
              </div>
            </div>
          </div>
        </div>
      </QuestionProvider>
    </AppStateProvider>
  );
}

export default App;
