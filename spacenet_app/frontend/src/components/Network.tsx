import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Container from 'react-bootstrap/Container'
import { useState } from 'react'
import SelectNetwork from './SelectNetwork'
import NetworkVis from './NetworkVis'

const Network = (props: {scenario: object, setScenario: Function, database: object, setDatabase: Function}) => {
    return (
      <Container fluid>
        <h2>Network</h2>
        <Row>
          <Col xs={4}>
            <SelectNetwork />
          </Col>
          <Col>
            <NetworkVis />
          </Col>
        </Row>
      </Container>
    )
  }
  
export default Network