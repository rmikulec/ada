import React, { createContext, useContext, useState, useCallback } from 'react';
import { postQuestion } from './Question';

const QuestionContext = createContext();

export const useQuestionContext = () => {
  return useContext(QuestionContext);
};

export const QuestionProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [response, setResponse] = useState(null)
  const [questions, setQuestions] = useState([])
  const [selectedQuestion, setSelectedQuestion] = useState(null)

  // Add a state variable for the question ID counter
  const [questionIdCounter, setQuestionIdCounter] = useState(1);

  const submitQuestion = useCallback(async (question) => {
    setLoading(true);
    setError(null);

    try {
      const response = await postQuestion(question);
      // You can handle the response as needed
      console.log(response)
      setResponse(response);

      const newQueston = {
        id: questionIdCounter,
        text: question,
        user: 'user',
        article: response.article.sections,
        references: response.references
      };
      setQuestions(oldQuestions => [...oldQuestions, newQueston])
      setSelectedQuestion(newQueston)
       // Increment the question ID counter for the next question
      setQuestionIdCounter(prevCounter => prevCounter + 1);
    } catch (error) {
      setError(error);
    } finally {
      setLoading(false);
    }
  }, [questionIdCounter]);


  const selectQuestion = useCallback(async (questionId) => {
    const selected = questions.find(question => question.id === questionId);
    setSelectedQuestion(selected);
  }, [questions]);

  return (
    <QuestionContext.Provider value={{ loading, error, response, questions, selectedQuestion, submitQuestion, selectQuestion }}>
      {children}
    </QuestionContext.Provider>
  );
};