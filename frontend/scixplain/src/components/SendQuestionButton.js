
import Button from 'react-bootstrap/Button';

import { useQuestionContext } from '../services/questionProvider';

function SendQuestionButton({onClick}) {
  const { loading, error, response, questions, submitQuestion } = useQuestionContext();


  return (
    <div className='send-question-button'>
        <Button
        variant="outline-success"
        disabled={loading}
        onClick={onClick}
        >
        {loading ? 'Loading…' : 'Ask!'}
        </Button>
    </div>
  );
}

export default SendQuestionButton;