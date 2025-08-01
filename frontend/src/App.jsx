// // import React from 'react';
// // import './App.css';
// // import ChatPage from './components/ChatPage';

// // function App() {
// //   return (
// //     <div className="chat-container">
// //       <div className="chat-header">
// //         🧠 AI Math Tutor
// //       </div>
// //       <ChatPage />
// //     </div>
// //   );
// // }

// // export default App;

// import React, { useState } from 'react';
// import './App.css';
// import ChatPage from './components/ChatPage';

// function App() {
//   // FIX: Lift state for collection name to the top level
//   const [collectionName, setCollectionName] = useState('gsm8k-base');
  
//   return (
//     <div className="chat-container">
//       <div className="chat-header">
//         <h1>🧠 AI Math Tutor</h1>
//         {/* FIX: Add the KB selection dropdown here */}
//         <div className="kb-selection-form">
//             <label htmlFor="kb-select">Active Knowledge Base:</label>
//             <select 
//                 id="kb-select" 
//                 value={collectionName} 
//                 onChange={(e) => setCollectionName(e.target.value)}
//             >
//                 <option value="gsm8k-base">GSM8K (Default)</option>
//                 <option value="math500-base">MATH-500</option>
//                 {/* You can add more pre-built KBs here */}
//                 {/* Dynamically created ones would require another API call to list collections */}
//             </select>
//         </div>
//       </div>
      
//       {/* FIX: Pass the selected collection name down to the ChatPage */}
//       <ChatPage selectedCollection={collectionName} />
//     </div>
//   );
// }

// export default App;

import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import SideBar from './components/SideBar';
import ChatPage from './components/ChatPage';

function App() {
  const [collectionName, setCollectionName] = useState('gsm8k-base');
  
  return (
    <Container fluid className="app-layout p-0">
      <Row className="g-0">
        <Col md={4} lg={3} className="sidebar">
          <SideBar 
            collectionName={collectionName} 
            setCollectionName={setCollectionName} 
          />
        </Col>
        <Col md={8} lg={9}>
          <ChatPage selectedCollection={collectionName} />
        </Col>
      </Row>
    </Container>
  );
}

export default App;