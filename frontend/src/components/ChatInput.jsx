// import React, { useState } from 'react';

// const ChatInput = ({ onSubmit, disabled }) => {
//   const [inputValue, setInputValue] = useState('');

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     onSubmit(inputValue);
//     setInputValue('');
//   };

//   return (
//     <form className="chat-input-form" onSubmit={handleSubmit}>
//       <input
//         type="text"
//         value={inputValue}
//         onChange={(e) => setInputValue(e.target.value)}
//         placeholder="Type your math problem here..."
//         disabled={disabled}
//       />
//       <button type="submit" disabled={disabled || !inputValue.trim()}>
//         Send
//       </button>
//     </form>
//   );
// };

// export default ChatInput;


import React, { useState } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import InputGroup from 'react-bootstrap/InputGroup';
import { SendFill } from 'react-bootstrap-icons';

const ChatInput = ({ onSubmit, disabled }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    onSubmit(inputValue);
    setInputValue('');
  };

  return (
    <Form onSubmit={handleSubmit}>
      <InputGroup>
        <Form.Control
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your math problem here..."
          disabled={disabled}
          className="rounded-pill"
        />
        <Button type="submit" variant="primary" className="rounded-pill ms-2" disabled={disabled || !inputValue.trim()}>
          <SendFill />
        </Button>
      </InputGroup>
    </Form>
  );
};

export default ChatInput;