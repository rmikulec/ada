// components/ExplainedDocument.js
import React from 'react';
import Markdown from 'react-markdown';
import { Spinner } from 'react-bootstrap'; // Import Spinner from react-bootstrap

import { useQuestionContext } from '../services/questionProvider';

const markdownContent = `
### Type your question and I'll do my best to answer it!
`;

function ExplainedDocument() {
  const { loading, error, response, questions, selectedQuestion, submitQuestion, selectQuestion } = useQuestionContext();
  const loadingMessage = 'Asking your question! This will take a minute...'

  return (
    <div className="explained-document">
      {loading ? (
        <div className="centered">
          <Spinner animation="border" role="status">
            <span className="sr-only">Loading...</span>
          </Spinner>
          <p>{loadingMessage}</p>
        </div>
      ) : response !== null ? (
        <Markdown>{selectedQuestion.answer}</Markdown>
      ) : (
        <Markdown>{markdownContent}</Markdown>
      )}
    </div>
  );
}

export default ExplainedDocument;
