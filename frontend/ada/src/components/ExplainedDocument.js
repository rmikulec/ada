// components/ExplainedDocument.js
import React from 'react';
import Markdown from 'react-markdown';
import { Spinner } from 'react-bootstrap'; // Import Spinner from react-bootstrap

import { useQuestionContext } from '../services/questionProvider';
import MarkdownImage from './MarkdownImage';

const markdownContent = `
### Type your question and I'll do my best to answer it!
`;

function ExplainedDocument() {
  const { loading, selectedQuestion } = useQuestionContext();
  const loadingMessage = 'Asking your question! This will take a minute...'

  return (
    <div className="explained-document">
    {loading ? (
      <div className="centered">
        <Spinner animation="border" role="status"/>
        <p>{loadingMessage}</p>
      </div>
    ) : selectedQuestion && Array.isArray(selectedQuestion.article) ? (
      selectedQuestion.article.map((section, index) => (
        <div key={index}>
          {section.image !== null ? (
            <MarkdownImage
              image={section.image}
              markdown={section.markdown}
            />
          ) : (
            <div class="markdown-article">
              <Markdown>{section.header}</Markdown>
              <Markdown>{section.markdown}</Markdown>
            </div>
          )}
        </div>
      ))
    ) : (
      <Markdown>{markdownContent}</Markdown>
    )}
  </div>

  );
}

export default ExplainedDocument;
