// import React, { useState, useEffect, useRef } from 'react';
// import Message from './Message';
// import ChatInput from './ChatInput';
// import FeedbackModal from './FeedbackModal';

// const API_URL = "http://localhost:8001";

// const ChatPage = ({selectedCollection}) => {
//   const [messages, setMessages] = useState([
//     { text: "Hello! Select a knowledge base and ask me a math problem.", from: 'ai', source: 'System' }
//   ]);
//   const [isLoading, setIsLoading] = useState(false);
//   const [modalData, setModalData] = useState(null);

//   // FIX: State for managing the selected knowledge base
//   const [collectionName, setCollectionName] = useState('gsm8k-base');
  
//   // FIX: State for the new KB creation form
//   const [newCollectionName, setNewCollectionName] = useState('');
//   const [pdfUrl, setPdfUrl] = useState('');
//   const [isCreatingKB, setIsCreatingKB] = useState(false);

//   const messagesEndRef = useRef(null);

//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   const handleSubmit = async (question) => {
//     if (!question.trim()) return;

//     setMessages(prev => [...prev, { text: question, from: 'user' }]);
//     setIsLoading(true);

//     try {
//       const response = await fetch(`${API_URL}/agent/ask`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           collection_name: selectedCollection, // Use the prop here
//           question: question
//         })
//       });
//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || "An error occurred.");
//       }

//       const data = await response.json();
//       setMessages(prev => [...prev, { text: data.answer, from: 'ai', source: data.source, question: question }]);
//     } catch (error) {
//       setMessages(prev => [...prev, { text: `Error: ${error.message}`, from: 'ai', source: 'Error' }]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleKBCreate = async (e) => {
//     e.preventDefault();
//     if (!newCollectionName.trim() || !pdfUrl.trim()) {
//       alert("Please provide a name and a valid URL for the new knowledge base.");
//       return;
//     }
//     setIsCreatingKB(true);
//     try {
//       await fetch(`${API_URL}/kb/create`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           collection_name: newCollectionName,
//           source_type: 'pdf_url',
//           source_name: pdfUrl
//         })
//       });
//       alert(`Knowledge base '${newCollectionName}' creation has started in the background. You can select it from the dropdown once it's ready (you may need to refresh).`);
//       setNewCollectionName('');
//       setPdfUrl('');
//     } catch (error) {
//       alert(`Error creating knowledge base: ${error.message}`);
//     } finally {
//       setIsCreatingKB(false);
//     }
//   };

//   // const openFeedbackModal = (originalQuestion, badAnswer) => {
//   //   setModalData({ question: originalQuestion, bad_answer: badAnswer });
//   // };

//   const openFeedbackModal = (originalQuestion, badAnswer) => {
//     setModalData({ question: originalQuestion, bad_answer: badAnswer });
//   };

//   const closeFeedbackModal = () => {
//     setModalData(null);
//   };

//   const handleFeedbackSubmit = async (correction) => {
//     await fetch(`${API_URL}/feedback/submit`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ ...modalData, correction })
//     });
//     alert("Thank you for your feedback!");
//     closeFeedbackModal();
//   };

//   return (
//     <>
//       <div className="messages-list">
//         {messages.map((msg, index) => (
//           <Message 
//             key={index} 
//             message={msg} 
//             onBadFeedback={openFeedbackModal}
//           />
//         ))}
//         {isLoading && <Message message={{ text: 'Thinking...', from: 'ai', source: 'System' }} />}
//         <div ref={messagesEndRef} />
//       </div>
      
//       {/* FIX: New section to create a KB */}
//       <div className="kb-create-section">
//         <h4>Create a New Knowledge Base from PDF URL</h4>
//         <form className="kb-create-form" onSubmit={handleKBCreate}>
//           <div>
//             <label>New KB Name (e.g., 'algebra-notes')</label>
//             <input 
//               type="text" 
//               value={newCollectionName}
//               onChange={(e) => setNewCollectionName(e.target.value)}
//               placeholder="A unique name, no spaces"
//               required
//             />
//           </div>
//           <div>
//             <label>Public PDF URL</label>
//             <input 
//               type="url" 
//               value={pdfUrl}
//               onChange={(e) => setPdfUrl(e.target.value)}
//               placeholder="https://example.com/math.pdf"
//               required
//             />
//           </div>
//           <button type="submit" disabled={isCreatingKB}>
//             {isCreatingKB ? 'Creating...' : 'Create KB'}
//           </button>
//         </form>
//       </div>

//       <ChatInput onSubmit={handleSubmit} disabled={isLoading} />
//       {modalData && (

//         <FeedbackModal
//           onSubmit={handleFeedbackSubmit}
//           onClose={closeFeedbackModal}
//         />
//       )}
//     </>
//   );
// };

// export default ChatPage;

import React, { useState, useEffect, useRef } from 'react';
import Card from 'react-bootstrap/Card';
import Stack from 'react-bootstrap/Stack';
import Spinner from 'react-bootstrap/Spinner';
import Message from './Message';
import ChatInput from './ChatInput';
import FeedbackModal from './FeedbackModal';

const API_URL = "http://localhost:8001";

const ChatPage = ({ selectedCollection }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [modalData, setModalData] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  
  const handleSubmit = async (question) => {
    if (!question.trim() || !selectedCollection) return;

    setMessages(prev => [...prev, { text: question, from: 'user' }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/agent/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ collection_name: selectedCollection, question: question })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "An error occurred.");
      }
      const data = await response.json();
      setMessages(prev => [...prev, { text: data.answer, from: 'ai', source: data.source, question: question }]);
    } catch (error) {
      setMessages(prev => [...prev, { text: `Error: ${error.message}`, from: 'ai', source: 'Error' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Card className="chat-card border-0">
        <Card.Header className="bg-light border-bottom">
          Active KB: <span className="fw-bold">{selectedCollection}</span>
        </Card.Header>
        <Card.Body className="messages-list p-4">
          <Stack gap={3}>
            {messages.length === 0 && <p className="text-center text-muted">Ask a math problem to get started.</p>}
            {messages.map((msg, index) => (
              <Message key={index} message={msg} onBadFeedback={setModalData} />
            ))}
            {isLoading && <Spinner animation="border" size="sm" />}
            <div ref={messagesEndRef} />
          </Stack>
        </Card.Body>
        <Card.Footer className="bg-light border-top p-3">
          <ChatInput onSubmit={handleSubmit} disabled={isLoading} />
        </Card.Footer>
      </Card>
      
      {modalData && (
        <FeedbackModal
          show={!!modalData}
          onHide={() => setModalData(null)}
          data={modalData}
          apiUrl={API_URL}
        />
      )}
    </>
  );
};

export default ChatPage;