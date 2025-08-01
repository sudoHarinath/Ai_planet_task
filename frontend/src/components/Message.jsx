// // import React from 'react';

// // const Message = ({ message, onBadFeedback }) => {
// //   const { text, from, source, question } = message;
// //   const isAI = from === 'ai';

// //   return (
// //     <div className={`message ${from}`}>
// //       {text}
// //       {isAI && source && (
// //         <div className="message-source">
// //           Answered from: <strong>{source}</strong>
// //         </div>
// //       )}
// //       {isAI && source !== 'System' && source !== 'Error' && (
// //         <div className="feedback-buttons">
// //           <button onClick={() => alert('Feedback received: Correct!')}>👍 Correct</button>
// //           <button onClick={() => onBadFeedback(question, text)}>👎 Incorrect</button>
// //         </div>
// //       )}
// //     </div>
// //   );
// // };

// // export default Message;


// import React, { useState, useMemo } from 'react';

// const Message = ({ message, onBadFeedback }) => {
//   const { text, from, source, question } = message;
//   const isAI = from === 'ai';

//   // State to control visibility of the thinking process
//   const [showThinking, setShowThinking] = useState(false);

//   // FIX: Parse the message to separate the thinking process from the main answer.
//   // useMemo ensures this parsing only happens once per message.
//   const { thinking, mainAnswer } = useMemo(() => {
//     if (!text || !isAI) {
//       return { thinking: null, mainAnswer: text };
//     }
//     const match = text.match(/<thinking>([\s\S]*?)<\/thinking>[\s\n]*(.*)/s);
//     if (match) {
//       // Return the thinking block and the final answer separately
//       return { thinking: match[1].trim(), mainAnswer: match[2].trim() };
//     }
//     // If no <thinking> tag, the whole message is the main answer
//     return { thinking: null, mainAnswer: text };
//   }, [text, isAI]);

//   return (
//     <div className={`message ${from}`}>
//       {mainAnswer}
      
//       {/* FIX: Use <details> and <summary> for a professional dropdown */}
//       {thinking && (
//         <details>
//           <summary>Show Reasoning</summary>
//           <div className="thinking-block">
//             <pre>{thinking}</pre>
//           </div>
//         </details>
//       )}

//       {isAI && source && (
//         <div className="message-source">
//           Answered from: <strong>{source}</strong>
//         </div>
//       )}

//       {isAI && source !== 'System' && source !== 'Error' && (
//         <div className="feedback-buttons">
//           <button onClick={() => alert('Feedback received: Correct!')}>👍 Correct</button>
//           <button onClick={() => onBadFeedback(question, mainAnswer)}>👎 Incorrect</button>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Message;

// import React, { useState, useMemo } from 'react';
// import Card from 'react-bootstrap/Card';
// import Button from 'react-bootstrap/Button';
// import Collapse from 'react-bootstrap/Collapse';
// import Stack from 'react-bootstrap/Stack';

// const Message = ({ message, onBadFeedback }) => {
//   const { text, from, source, question } = message;
//   const isAI = from === 'ai';
//   const [showThinking, setShowThinking] = useState(false);

//   const { thinking, mainAnswer } = useMemo(() => {
//     if (!text || !isAI) return { thinking: null, mainAnswer: text };
//     const match = text.match(/<thinking>([\s\S]*?)<\/thinking>[\s\n]*(.*)/s);
//     if (match) return { thinking: match[1].trim(), mainAnswer: match[2].trim() || "(See reasoning for answer)" };
//     return { thinking: null, mainAnswer: text };
//   }, [text, isAI]);
  
//   const alignClass = isAI ? 'me-auto' : 'ms-auto';

//   return (
//     <div className={`message-container ${alignClass}`}>
//       <Card className={`message-bubble ${from} p-2 px-3 rounded-3`}>
//         <Card.Body className="p-1">
//           <p className="mb-0">{mainAnswer}</p>
//           {thinking && (
//             <Button
//               onClick={() => setShowThinking(!showThinking)}
//               aria-controls="thinking-collapse-text"
//               aria-expanded={showThinking}
//               variant="link"
//               size="sm"
//               className="text-decoration-none p-0 mt-2 reasoning-button"
//             >
//               {showThinking ? 'Hide Reasoning' : 'Show Reasoning'}
//             </Button>
//           )}
//           <Collapse in={showThinking}>
//             <div id="thinking-collapse-text" className="mt-2">
//               <div className="thinking-block">
//                 <pre>{thinking}</pre>
//               </div>
//             </div>
//           </Collapse>
//         </Card.Body>
//         {isAI && source && (
//           <Card.Footer className="bg-transparent border-top-0 pt-0 pb-1 px-1">
//             <small className="text-muted">From: {source}</small>
//             <Stack direction="horizontal" gap={2} className="mt-2">
//                <Button variant="outline-secondary" size="sm" onClick={() => alert('Feedback: Correct!')}>👍</Button>
//                <Button variant="outline-secondary" size="sm" onClick={() => onBadFeedback({ question, bad_answer: mainAnswer })}>👎</Button>
//             </Stack>
//           </Card.Footer>
//         )}
//       </Card>
//     </div>
//   );
// };

// export default Message;


import React, { useState, useMemo, useRef, useEffect } from 'react';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import Collapse from 'react-bootstrap/Collapse';
import Stack from 'react-bootstrap/Stack';

const Message = ({ message, onBadFeedback }) => {
  const { text, from, source, question } = message;
  const isAI = from === 'ai';
  const [showThinking, setShowThinking] = useState(false);
  const thinkingRef = useRef(null);

  const { thinking, mainAnswer } = useMemo(() => {
    if (!text || !isAI) return { thinking: null, mainAnswer: text };
    const match = text.match(/<thinking>([\s\S]*?)<\/thinking>[\s\n]*(.*)/s);
    if (match) {
      return {
        thinking: match[1].trim(),
        mainAnswer: match[2].trim() || '(See reasoning for answer)'
      };
    }
    return { thinking: null, mainAnswer: text };
  }, [text, isAI]);

  useEffect(() => {
    if (showThinking && thinkingRef.current) {
      const { top } = thinkingRef.current.getBoundingClientRect();
      const available = window.innerHeight - top - 16;
      thinkingRef.current.style.maxHeight = `${available}px`;
      thinkingRef.current.style.overflowY = 'auto';
    }
  }, [showThinking]);

  const alignClass = isAI ? 'me-auto' : 'ms-auto';

  return (
    <div className={`message-container ${alignClass}`}>
      <Card className={`message-bubble ${from} p-2 px-3 rounded-3`}>
        <Card.Body className="p-1">
          <p className="mb-0">{mainAnswer}</p>
          {thinking && (
            <Button
              onClick={() => setShowThinking(!showThinking)}
              aria-controls="thinking-collapse-text"
              aria-expanded={showThinking}
              variant="link"
              size="sm"
              className="text-decoration-none p-0 mt-2 reasoning-button"
            >
              {showThinking ? 'Hide Reasoning' : 'Show Reasoning'}
            </Button>
          )}
          <Collapse in={showThinking}>
            <div
              ref={thinkingRef}
              id="thinking-collapse-text"
              className="mt-2 thinking-block"
              style={{ maxWidth: '90ch', overflowWrap: 'break-word' }}
            >
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {thinking}
              </pre>
            </div>
          </Collapse>
        </Card.Body>
        {isAI && source && (
          <Card.Footer className="bg-transparent border-top-0 pt-0 pb-1 px-1">
            <small className="text-muted">From: {source}</small>
            <Stack direction="horizontal" gap={2} className="mt-2">
              <Button variant="outline-secondary" size="sm" onClick={() => alert('Feedback: Correct!')}>👍</Button>
              <Button variant="outline-secondary" size="sm" onClick={() => onBadFeedback({ question, bad_answer: mainAnswer })}>👎</Button>
            </Stack>
          </Card.Footer>
        )}
      </Card>
    </div>
  );
};

export default Message;
