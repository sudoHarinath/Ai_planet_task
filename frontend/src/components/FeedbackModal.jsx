// import React, { useState } from 'react';

// const FeedbackModal = ({ onSubmit, onClose }) => {
//   const [correction, setCorrection] = useState('');

//   return (
//     <>
//       <div className="modal-overlay" onClick={onClose}></div>
//       <div className="feedback-modal">
//         <h3>Provide Correction</h3>
//         <p>Please provide the correct answer or reasoning below.</p>
//         <textarea
//           rows="5"
//           style={{ width: '100%', padding: '8px' }}
//           value={correction}
//           onChange={(e) => setCorrection(e.target.value)}
//         ></textarea>
//         <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
//           <button onClick={onClose} style={{ marginRight: '8px' }}>Cancel</button>
//           <button onClick={() => onSubmit(correction)}>Submit</button>
//         </div>
//       </div>
//     </>
//   );
// };

// export default FeedbackModal;


import React, { useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

const FeedbackModal = ({ show, onHide, data, apiUrl }) => {
  const [correction, setCorrection] = useState('');
  
  const handleSubmit = async () => {
    await fetch(`${apiUrl}/feedback/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, correction })
    });
    alert("Thank you for your feedback!");
    onHide();
  };

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Provide Correction</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p><strong>Original Question:</strong> {data.question}</p>
        <Form.Group controlId="correction-text">
          <Form.Label>What is the correct answer or reasoning?</Form.Label>
          <Form.Control
            as="textarea"
            rows={4}
            value={correction}
            onChange={(e) => setCorrection(e.target.value)}
          />
        </Form.Group>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit}>
          Submit Feedback
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default FeedbackModal;