import Togglable from '../components/Togglable'
import CurrentScenario from '../components/CurrentScenario'
import { Outlet } from 'react-router-dom'

const Scenario = (props: {scenario: object, setScenario: Function, database: object, setDatabase: Function}) => {
    return (
    <div>
        <Togglable buttonLabel="Current Scenario Info">
            <CurrentScenario 
                scenario={props.scenario} 
                setScenario={props.setScenario} 
                database={props.database} 
                setDatabase={props.setDatabase}
            />
        </Togglable>
        <hr></hr>
        <Outlet />
    </div>
    )
}

export default Scenario