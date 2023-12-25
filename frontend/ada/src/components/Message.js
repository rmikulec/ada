import React from 'react';
import { IoBookOutline } from 'react-icons/io5';

import { useAppStateContext } from '../services/appProvider';

import './Message.css'


function Message({ id, text, isSelected, onClick }) {
  const messageClass = isSelected ? 'user' : 'chatbot';
  const messageID = id
  const { showRefs, setShowRefs }  = useAppStateContext();


  const handleClick = () => {
    // Call the onClick function when a message is clicked
    console.log(text)
    onClick(messageID);
  };

  const handleBookClick = () => {
    setShowRefs(true)
  }

  return (
    <div 
      className={`message ${messageClass}`} 
      onClick={handleClick}
      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pointerEvents: 'auto' }}
    >
      <p>{text}</p>
      <IoBookOutline onClick={handleBookClick} style={{ cursor: 'pointer' }} /> {/* Book Icon */}
    </div>
  );
}

export default Message;
