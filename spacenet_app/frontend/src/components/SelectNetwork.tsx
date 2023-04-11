import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Container from 'react-bootstrap/Container'
import { useState } from 'react'

const SelectNetwork = () => {
    return (
      <Container fluid>
        <Row className="mb-3">
          <h4>Select Nodes:</h4>
        </Row>
        <Row>
          <h4>Select Edges:</h4>
        </Row>
      </Container>
    )
  }
  
export default SelectNetwork