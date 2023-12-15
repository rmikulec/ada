import React from 'react';

function Message({ id, text, isSelected, onClick }) {
  const messageClass = isSelected ? 'user' : 'chatbot';
  const messageID = id
  const handleClick = () => {
    // Call the onClick function when a message is clicked
    console.log(text)
    onClick(messageID);
  };

  return (
    <div 
      className={`message ${messageClass}`} 
      onClick={handleClick}
      style={{ pointerEvents: 'auto' }}
    >
      <p>{text}</p>
    </div>
  );
}

export default Message;
