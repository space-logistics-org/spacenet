import Container from 'react-bootstrap/Container'
import NavBar from './components/NavBar'
import {
  Routes, Route
} from 'react-router-dom'
import Scenario from './pages/Scenario'
import Home from './pages/Home'
import Network from './components/Network'
import Missions from './components/Missions'
import { useState } from 'react'


const App = () => {
  const [scenario, setScenario] = useState({})
  const [database, setDatabase] = useState({})


  return (
    <Container fluid>
      <NavBar/>
      <Routes>
        <Route path="scenario" element={ 
          <Scenario 
            scenario={scenario} 
            setScenario={setScenario} 
            database={database} 
            setDatabase={setDatabase}
          /> 
          }>
            <Route index element={
              <Network 
                scenario={scenario} 
                setScenario={setScenario} 
                database={database} 
                setDatabase={setDatabase}
              />
            } />
            <Route path="network" element={
              <Network 
                scenario={scenario} 
                setScenario={setScenario} 
                database={database} 
                setDatabase={setDatabase}
              />} 
            />
            <Route path="missions" element={ 
              <Missions 
                scenario={scenario} 
                setScenario={setScenario} 
                database={database} 
                setDatabase={setDatabase}
              /> } 
            />
        </Route>
        <Route index element={<Home />} />
        <Route path="*" element={<Home />} />
      </Routes>

      <footer className="footer fixed-bottom">
        <i>SpaceNet Cloud 2023</i>
      </footer>
  </Container>

  )
}

export default App