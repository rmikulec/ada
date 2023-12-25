import React, { useState } from 'react';
import { IoArrowDownCircle, IoImageOutline, IoDocumentOutline, IoGlobeOutline } from 'react-icons/io5';


const Reference = ({ type, name, link }) => {
  const [isOpen, setOpen] = useState(false);

  // Function to toggle open state
  const toggleOpen = () => setOpen(!isOpen);

  // Determining the color and icon based on the reference type
  let color, Icon;
  switch (type) {
    case 'Web Article':
      color = 'blue';
      Icon = IoGlobeOutline;
      break;
    case 'Image':
      color = 'green';
      Icon = IoImageOutline;
      break;
    case 'Research Paper':
      color = 'red';
      Icon = IoDocumentOutline;
      break;
    default:
      color = 'grey';
      Icon = IoDocumentOutline;
  }

  return (
<div
      className={`reference-item ${isOpen ? 'open' : ''}`}
      style={{
        display: 'flex',
        flexDirection: 'column', // Changed to column to stack elements
        cursor: 'pointer',
        border: `1px solid ${color}`,
        borderRadius: '5px',
        padding: '10px',
        marginBottom: '10px',
      }}
      onClick={toggleOpen}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start', // Align items to the start to accommodate wrapping text
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <div style={{ fontSize: '20px', flexShrink: 0, marginRight: '10px' }}>
            <Icon style={{ color }} />
          </div>
          <p style={{ 
              margin: 0, 
              fontSize: '16px', 
              flex: 1, // Allow text to fill the space
              wordBreak: 'break-word' // Break the word to ensure wrapping
            }}>
            {name}
          </p>
        </div>
        <IoArrowDownCircle
          style={{ fontSize: '20px', transition: 'transform 0.3s', transform: `rotate(${isOpen ? '180deg' : '0deg'})`, flexShrink: 0 }}
        />
      </div>
      {isOpen && (
        <div
          style={{
            marginTop: '10px',
            borderTop: `1px solid ${color}`,
            paddingTop: '10px',
            display: 'flex',
            flexDirection: 'column', // Ensure layout is column for the expanded content
          }}
        >
          <a href={link} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: color }}>
            Link
          </a> {/* This is your clickable hyperlink */}
        </div>
      )}
    </div>
  );
};

export default Reference;
