import Container from 'react-bootstrap/Container'
import Nav from 'react-bootstrap/Nav'
import Navbar from 'react-bootstrap/Navbar'
import { LinkContainer } from 'react-router-bootstrap'
import Image from 'react-bootstrap/Image'
import { NavDropdown } from 'react-bootstrap'

const NavBar = () => {

  return (
    <Navbar bg="light" expand="lg">
      <Container>
        <Image className="m-2" style={{ width: 40 }} src="/SpaceNetLogo.jpg"></Image>
        <LinkContainer to="/">
          <Navbar.Brand>SpaceNet Cloud</Navbar.Brand>
        </LinkContainer>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav>
            <NavDropdown title="Scenario">
              <NavDropdown.Item>
                <LinkContainer className="me-auto" to="scenario/network">
                  <Nav.Link>Network</Nav.Link>
                </LinkContainer>
              </NavDropdown.Item>
              <NavDropdown.Item>
                <LinkContainer className="me-auto" to="scenario/missions">
                  <Nav.Link>Missions</Nav.Link>
                </LinkContainer>
              </NavDropdown.Item>
            </NavDropdown>

          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  )
}

export default NavBar


