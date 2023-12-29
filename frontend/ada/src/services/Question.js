import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';

export const postQuestion = async (question) => {
  try {
    const questionData = {question:question}
    const response = await axios.post(`${BASE_URL}/ask  `, questionData);
    return response.data;
  } catch (error) {
    throw error;
  }
};