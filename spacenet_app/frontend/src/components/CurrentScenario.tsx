/* eslint-disable react/display-name */
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Container from 'react-bootstrap/Container'
import { useState } from 'react'
import Configuration from './Configuration'
import Database from './Database'


const CurrentScenario = (props: {scenario: object, setScenario: Function, database: object, setDatabase: Function}) => {
    const [scenarioInfo, setScenarioInfo] = useState({
        name: '',
        createdBy: '',
        description: '',
        startDate: new Date().toISOString().slice(0,19),
        scenarioType: ''
    })

    return (
        <Container fluid>
          <h4 className="mt-3">Current Scenario</h4>
          <Row className="mt-3 mb-3">
            <Col xs={2}>
              <Button variant="primary">Export Scenario</Button>
            </Col>
            <Col xs={3}>
              <Button variant="danger">Upload New Scenario</Button>
            </Col>
            <Col xs={3}>
              <Configuration scenario={props.scenario} setScenario={props.setScenario} />
            </Col>
            <Col xs={3}>
              <Database database={props.database} setDatabase={props.setDatabase}/>
            </Col>
          </Row>
          <Row>
            <Col>
              <Form>
                <Row className="mb-3">
                  <Form.Group as={Col}>
                    <Form.Label>Name</Form.Label>
                    <Form.Control id="name" value={scenarioInfo.name} onChange={({ target }) => setScenarioInfo({ ...scenarioInfo, name: target.value })} type="text" placeholder="Enter name" />
                  </Form.Group>
                  <Form.Group as={Col}>
                    <Form.Label>Created by</Form.Label>
                    <Form.Control id="createdBy" as="textarea" placeholder="Enter created by" value={scenarioInfo.createdBy} onChange={({ target }) => setScenarioInfo({ ...scenarioInfo, createdBy: target.value })}/>
                  </Form.Group>
                  <Form.Group as={Col}>
                    <Form.Label>Description</Form.Label>
                    <Form.Control id="description" as="textarea" placeholder="Enter description" value={scenarioInfo.description} onChange={({ target }) => setScenarioInfo({ ...scenarioInfo, description: target.value })}/>
                  </Form.Group>
                </Row>
                <Row className="mb-3">
                  <Form.Group as={Col}>
                    <Form.Label>Start date</Form.Label>
                    <Form.Control id="startDate" value={scenarioInfo.startDate} onChange={({ target }) => setScenarioInfo({ ...scenarioInfo, startDate: target.value })} type="datetime-local" placeholder="Enter date" />
                  </Form.Group>
                  <Form.Group as={Col}>
                    <Form.Label>Scenario Type</Form.Label>
                    <Form.Select id="scenarioType" className="typeSelect" value={scenarioInfo.scenarioType} onChange={({ target }) => setScenarioInfo({ ...scenarioInfo, scenarioType: target.value })}>
                      <option>Choose...</option>
                      <option value="Moon-only">Moon Only</option>
                      <option value="Mars-only">Mars Only</option>
                      <option value="ISS">ISS</option>
                      <option value="Lunar">Lunar</option>
                      <option value="Martian">Martian</option>
                      <option value="Solar System">Solar System</option>
                    </Form.Select>
                  </Form.Group>
                </Row>
              </Form>
            </Col>
          </Row>
        </Container>
      )
}

export default CurrentScenario