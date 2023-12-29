import React, { useState, useRef, useEffect } from 'react';
import { IoArrowDownCircleOutline, IoImageOutline, IoDocumentOutline, IoGlobeOutline, IoHelpCircleOutline } from 'react-icons/io5';

const Reference = ({ type, name, link }) => {
  const [isOpen, setOpen] = useState(false);
  const [maxHeight, setMaxHeight] = useState("0px");
  const contentRef = useRef(null);

  // Function to toggle open state and set maxHeight
  const toggleOpen = () => {
    // If opening, set maxHeight to the content's scrollHeight
    if (!isOpen) {
      setMaxHeight(`${contentRef.current.scrollHeight}px`);
    } else {
      // If closing, reset maxHeight to 0
      setMaxHeight("0px");
    }
    setOpen(!isOpen);
  };

  useEffect(() => {
    // Adjust max height when window resizes
    const handleResize = () => {
      if (isOpen && contentRef.current) {
        setMaxHeight(`${contentRef.current.scrollHeight}px`);
      }
    };

    // Adjust max height immediately if isOpen is true on initial render
    if (isOpen && contentRef.current) {
      setMaxHeight(`${contentRef.current.scrollHeight}px`);
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isOpen]); // Only re-run the effect if isOpen changes

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
      Icon = IoHelpCircleOutline;
  }

  return (
    <div
      className={`reference-item ${isOpen ? 'open' : ''}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        border: `1px solid ${color}`,
        color: {color},
        borderRadius: '5px',
        padding: '10px',
        marginBottom: '10px',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <Icon style={{ fontSize: '20px', color, marginRight: '10px', flexShrink: 0 }} />
          <p style={{ margin: 0, fontSize: '16px', flex: 1, wordBreak: 'break-word' }}>
            {name}
          </p>
        </div>
        <IoArrowDownCircleOutline
          onClick={toggleOpen} // Only the arrow is clickable to toggle
          style={{ fontSize: '20px', transition: 'transform 0.3s', transform: `rotate(${isOpen ? '180deg' : '0deg'})`, cursor: 'pointer' }}
        />
      </div>
      <div
        ref={contentRef}
        style={{
          maxHeight, // Dynamic max-height for transition
          transition: 'max-height 0.2s ease-in-out', // Smooth transition for max-height
          overflow: 'hidden', // Hide the overflow content
        }}
      >
        <a href={link} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: color }}>
          Link
        </a>
      </div>
    </div>
  );
};

export default Reference;
