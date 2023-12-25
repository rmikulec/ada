import React from 'react';
import { IoBookOutline } from 'react-icons/io5';
import { useAppStateContext } from '../services/appProvider';

function Message({ id, text, isSelected, onClick }) {
  const messageClass = isSelected ? 'user' : 'chatbot';
  const messageID = id;
  const { setShowRefs } = useAppStateContext();

  const handleClick = () => {
    // Call the onClick function when a message is clicked
    console.log(text);
    onClick(messageID);
  };

  const handleBookClick = (e) => {
    e.stopPropagation(); // Prevent the message click event when clicking the book
    setShowRefs(true);
  };

  return (
    <div 
      className={`message ${messageClass}`} 
      onClick={handleClick}
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        cursor: 'pointer',
        border: '1px solid green', // Static green border
        borderRadius: '5px',
        padding: '10px',
        marginBottom: '10px',
        overflow: 'hidden', // Similar to the Reference component
      }}
    >
      <p style={{ 
        margin: 0, 
        flex: 1, 
        wordBreak: 'break-word' // To ensure text wrapping similar to the Reference component
      }}>{text}</p>
      <IoBookOutline onClick={handleBookClick} style={{ fontSize: '20px', cursor: 'pointer', marginLeft: '10px' }} /> {/* Book Icon */}
    </div>
  );
}

export default Message;
