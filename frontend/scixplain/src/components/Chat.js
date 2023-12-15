// components/Chat.js
import './Chat.css';

import React, { useState } from 'react';
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { Container, Row, Col, Form } from 'react-bootstrap'; // Import Spinner from react-bootstrap
import Message from './Message';

import { useQuestionContext } from '../services/questionProvider';
import SendQuestionButton from './SendQuestionButton';

function Chat() {
  const [question, setQuestion] = useState([]);
  const { loading, error, response, questions, selectedQuestion, submitQuestion, selectQuestion } = useQuestionContext();

  const handleSubmitQuestion = async () => {
    if (question.trim() === '') {
      // You can add validation logic here to ensure the question is not empty
      return;
    }

    try {
      await submitQuestion(question);
      // Optionally, you can perform additional actions after successful submission
      setQuestion(''); // Clear the input field
    } catch (error) {
      // Handle any errors that may occur during submission
      console.error('Error submitting question:', error.message);
    }
  };


  const handleSelectQuestion = async (id) => {
    selectQuestion(id)
    console.log(selectedQuestion)
  }

  return (
    <Container className="chat-container">
      <Row>
        <Col>
          <div className="chat-box">
          <TransitionGroup>
            {questions.map((question) => (
            <CSSTransition
              key={question.id}
              timeout={500}
              classNames="message"
            >
              <Message 
                key={question.id}
                id={question.id}
                text={question.text}
                isSelected={selectedQuestion.id === question.id}
                onClick={handleSelectQuestion}
              />
              </CSSTransition>
            ))}
            </TransitionGroup>
          </div>
          <Form className="message-input">
            <Form.Group as={Row}>
              <Col>
                <Form.Control
                  type="text"
                  placeholder="Ask a question..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="form-control"
                />
              </Col>
              <Col>
                <SendQuestionButton onClick={handleSubmitQuestion}/>
              </Col>
            </Form.Group>
          </Form>
        </Col>
      </Row>
    </Container>
  );
}

export default Chat;
