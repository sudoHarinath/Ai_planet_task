// import React, { useState, useEffect } from 'react';
// import Form from 'react-bootstrap/Form';
// import Button from 'react-bootstrap/Button';
// import Card from 'react-bootstrap/Card';
// import Stack from 'react-bootstrap/Stack';

// const API_URL = "http://localhost:8001"; // Make sure your FastAPI port is correct

// const SideBar = ({ collectionName, setCollectionName }) => {
//   // State for the dynamic list of KBs
//   const [kbList, setKbList] = useState([]);

//   // State for the 'Create New KB' form
//   const [newCollectionName, setNewCollectionName] = useState('');
//   const [pdfUrl, setPdfUrl] = useState('');
//   const [pdfFile, setPdfFile] = useState(null);
//   const [uploadMode, setUploadMode] = useState('file'); // 'file' or 'url'
//   const [isCreatingKB, setIsCreatingKB] = useState(false);

//   // Function to fetch the list of available KBs from the backend
//   const fetchKbList = async () => {
//     try {
//       const response = await fetch(`${API_URL}/kb/list`);
//       if (!response.ok) {
//         throw new Error(`HTTP error! status: ${response.status}`);
//       }
//       const data = await response.json();
      
//       // Add the default KBs to the list if they aren't already there and sort them
//       const defaults = ["gsm8k-base", "math500-base"];
//       const combined = [...new Set([...defaults, ...data.collections])].sort();
//       setKbList(combined);
//     } catch (error) {
//       console.error("Failed to fetch KB list:", error);
//       // Fallback to defaults if the fetch fails
//       setKbList(["gsm8k-base", "math500-base"]);
//     }
//   };

//   // Fetch the KB list when the component first loads
//   useEffect(() => {
//     fetchKbList();
//   }, []);

//   // Handler for the create KB form submission
//   const handleKBCreate = async (e) => {
//     e.preventDefault();
//     if (!newCollectionName.trim()) {
//       alert("Please provide a name for the new knowledge base.");
//       return;
//     }
    
//     // Use FormData to handle file uploads
//     const formData = new FormData();
//     formData.append('collection_name', newCollectionName);

//     if (uploadMode === 'file' && pdfFile) {
//       formData.append('source_type', 'pdf_file');
//       formData.append('file', pdfFile);
//     } else if (uploadMode === 'url' && pdfUrl) {
//       formData.append('source_type', 'pdf_url');
//       formData.append('source_name', pdfUrl);
//     } else {
//       alert("Please provide a PDF file or a URL.");
//       return;
//     }

//     setIsCreatingKB(true);
//     try {
//       await fetch(`${API_URL}/kb/create`, { method: 'POST', body: formData });
//       alert(`Knowledge base '${newCollectionName}' creation has started. It will be available in the dropdown shortly.`);
      
//       // After successfully starting the creation, refresh the KB list and auto-select the new one
//       await fetchKbList();
//       setCollectionName(newCollectionName);

//       // Reset the form fields
//       setNewCollectionName('');
//       setPdfUrl('');
//       setPdfFile(null);
      
//     } catch (error) {
//       alert(`Error creating knowledge base: ${error.message}`);
//     } finally {
//       setIsCreatingKB(false);
//     }
//   };

//   return (
//     <Stack gap={4}>
//       <div className="title-section">
//         <h2 className="h4 mb-0 fw-bold">🧠 AI Math Tutor</h2>
//       </div>
      
//       <Form.Group controlId="kb-select">
//         <Form.Label className="fw-bold">Active Knowledge Base</Form.Label>
//         <Form.Select 
//           value={collectionName} 
//           onChange={(e) => setCollectionName(e.target.value)}
//         >
//           {kbList.map(kb => (
//             <option key={kb} value={kb}>
//               {kb}
//             </option>
//           ))}
//         </Form.Select>
//       </Form.Group>

//       {/* The "Create New KB" Card and Form */}
//       <Card>
//         <Card.Body>
//           <Card.Title className="h6">Create New Knowledge Base</Card.Title>
//           <Form onSubmit={handleKBCreate}>
//             <Stack gap={3}>
//               <Form.Group controlId="new-kb-name">
//                 <Form.Label>New KB Name</Form.Label>
//                 <Form.Control 
//                   type="text" 
//                   value={newCollectionName}
//                   onChange={(e) => setNewCollectionName(e.target.value)}
//                   placeholder="e.g., algebra-notes"
//                   required
//                 />
//               </Form.Group>

//               <Form.Group>
//                 <Form.Check inline type="radio" id="file-mode" label="Upload PDF" name="uploadMode" value="file" checked={uploadMode === 'file'} onChange={() => setUploadMode('file')} />
//                 <Form.Check inline type="radio" id="url-mode" label="From URL" name="uploadMode" value="url" checked={uploadMode === 'url'} onChange={() => setUploadMode('url')} />
//               </Form.Group>

//               {uploadMode === 'file' ? (
//                 <Form.Group controlId="pdf-file">
//                   <Form.Control type="file" accept=".pdf" onChange={(e) => setPdfFile(e.target.files[0])} required={uploadMode === 'file'} />
//                 </Form.Group>
//               ) : (
//                 <Form.Group controlId="pdf-url">
//                   <Form.Control type="url" value={pdfUrl} onChange={(e) => setPdfUrl(e.target.value)} placeholder="https://example.com/math.pdf" required={uploadMode === 'url'} />
//                 </Form.Group>
//               )}
              
//               <Button variant="primary" type="submit" disabled={isCreatingKB} className="mt-2">
//                 {isCreatingKB ? 'Creating...' : 'Create KB'}
//               </Button>
//             </Stack>
//           </Form>
//         </Card.Body>
//       </Card>
//     </Stack>
//   );
// };

// export default SideBar;


import React, { useState, useEffect } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import Stack from 'react-bootstrap/Stack';
import { Gear } from 'react-bootstrap-icons';

const API_URL = "http://localhost:8001"; // Make sure your FastAPI port is correct

const SideBar = ({ collectionName, setCollectionName }) => {
  const [kbList, setKbList] = useState([]);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [pdfUrl, setPdfUrl] = useState('');
  const [pdfFile, setPdfFile] = useState(null);
  const [uploadMode, setUploadMode] = useState('file');
  const [isCreatingKB, setIsCreatingKB] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false); // NEW: State for optimization button

  const fetchKbList = async () => {
    try {
      const response = await fetch(`${API_URL}/kb/list`);
      const data = await response.json();
      const defaults = ["gsm8k-base", "math500-base"];
      const combined = [...new Set([...defaults, ...data.collections])].sort();
      setKbList(combined);
    } catch (error) {
      console.error("Failed to fetch KB list:", error);
      setKbList(["gsm8k-base", "math500-base"]);
    }
  };

  useEffect(() => {
    fetchKbList();
  }, []);

  const handleKBCreate = async (e) => {
    e.preventDefault();
    if (!newCollectionName.trim()) {
      alert("Please provide a name for the new knowledge base.");
      return;
    }
    const formData = new FormData();
    formData.append('collection_name', newCollectionName);
    if (uploadMode === 'file' && pdfFile) {
      formData.append('source_type', 'pdf_file');
      formData.append('file', pdfFile);
    } else if (uploadMode === 'url' && pdfUrl) {
      formData.append('source_type', 'pdf_url');
      formData.append('source_name', pdfUrl);
    } else {
      alert("Please provide a PDF file or a URL.");
      return;
    }
    setIsCreatingKB(true);
    try {
      await fetch(`${API_URL}/kb/create`, { method: 'POST', body: formData });
      alert(`Knowledge base '${newCollectionName}' creation started.`);
      await fetchKbList();
      setCollectionName(newCollectionName);
      setNewCollectionName('');
      setPdfUrl('');
      setPdfFile(null);
    } catch (error) {
      alert(`Error creating knowledge base: ${error.message}`);
    } finally {
      setIsCreatingKB(false);
    }
  };

  // NEW: Handler to call the optimization endpoint
  const handleOptimize = async () => {
    if (!window.confirm("This will start the optimization process based on all collected feedback. It may take several minutes and consume resources. Continue?")) {
      return;
    }
    setIsOptimizing(true);
    try {
      await fetch(`${API_URL}/agent/optimize`, { method: 'POST' });
      alert("Agent optimization started! The agent will use an improved prompt after the process completes and the server is restarted.");
    } catch (error) {
      alert(`Error starting optimization: ${error.message}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <Stack gap={4}>
      <div className="title-section">
        <h2 className="h4 mb-0 fw-bold">🧠 AI Math Tutor</h2>
      </div>
      
      <Form.Group controlId="kb-select">
        <Form.Label className="fw-bold">Active Knowledge Base</Form.Label>
        <Form.Select 
          value={collectionName} 
          onChange={(e) => setCollectionName(e.target.value)}
        >
          {kbList.map(kb => (
            <option key={kb} value={kb}>{kb}</option>
          ))}
        </Form.Select>
      </Form.Group>

      <Card>
        <Card.Body>
          <Card.Title className="h6">Create New Knowledge Base</Card.Title>
          <Form onSubmit={handleKBCreate}>
            <Stack gap={3}>
              <Form.Group controlId="new-kb-name">
                <Form.Label>New KB Name</Form.Label>
                <Form.Control type="text" value={newCollectionName} onChange={(e) => setNewCollectionName(e.target.value)} placeholder="e.g., calculus-101" required />
              </Form.Group>
              <Form.Group>
                <Form.Check inline type="radio" id="file-mode" label="Upload PDF" name="uploadMode" value="file" checked={uploadMode === 'file'} onChange={() => setUploadMode('file')} />
                <Form.Check inline type="radio" id="url-mode" label="From URL" name="uploadMode" value="url" checked={uploadMode === 'url'} onChange={() => setUploadMode('url')} />
              </Form.Group>
              {uploadMode === 'file' ? (
                <Form.Group controlId="pdf-file"><Form.Control type="file" accept=".pdf" onChange={(e) => setPdfFile(e.target.files[0])} required={uploadMode === 'file'} /></Form.Group>
              ) : (
                <Form.Group controlId="pdf-url"><Form.Control type="url" value={pdfUrl} onChange={(e) => setPdfUrl(e.target.value)} placeholder="https://example.com/math.pdf" required={uploadMode === 'url'} /></Form.Group>
              )}
              <Button variant="primary" type="submit" disabled={isCreatingKB} className="mt-2">{isCreatingKB ? 'Creating...' : 'Create KB'}</Button>
            </Stack>
          </Form>
        </Card.Body>
      </Card>

      {/* NEW: Card for triggering the optimization */}
      <Card>
        <Card.Body>
          <Card.Title className="h6">Agent Self-Improvement</Card.Title>
          <Card.Text className="small text-muted">
            Use collected feedback to optimize the agent's performance. This process can be resource-intensive.
          </Card.Text>
          <Button variant="success" onClick={handleOptimize} disabled={isOptimizing}>
            <Gear className="me-2" />
            {isOptimizing ? 'Optimizing...' : 'Optimize with Feedback'}
          </Button>
        </Card.Body>
      </Card>
    </Stack>
  );
};

export default SideBar;
