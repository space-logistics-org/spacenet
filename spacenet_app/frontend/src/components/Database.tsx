import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';

const Database = (props: {database: object, setDatabase: Function}) => {
  const [show, setShow] = useState(false)

  const handleClose = () => setShow(false)
  const handleShow = () => setShow(true)

  return (
    <>
    {props.database ?
        <Button variant="outline-dark" onClick={handleShow}>
            Upload Database
        </Button>
        :
        <div>
          <Button variant="outline-dark" onClick={handleShow}>
            Edit Database
          </Button>
        </div>
    }
      

      <Modal
        show={show}
        onHide={handleClose}
        backdrop="static"
        keyboard={false}
      >
        <Modal.Header closeButton>
          <Modal.Title>Edit Database</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Modal for uploading database if one is not already added, or switching to a different database.
        </Modal.Body>
        <Modal.Footer>
          <input type="file" onChange={(event) => {console.log('file uploaded'); console.log(event.target.files ? typeof event.target.files[0] : 'ww'); props.setDatabase(event.target.files ? event.target.files[0] : null)}}  name="database" accept=".xlsx" className="form-control"/>
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleClose} type="submit">Save</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default Database