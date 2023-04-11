import Button from 'react-bootstrap/Button'
import Image from 'react-bootstrap/Image'
import { useState, forwardRef, useImperativeHandle } from 'react'

const Togglable = forwardRef((props: {buttonLabel: string, children: any}, refs) => {
  const [visible, setVisible] = useState(false)

  const hideWhenVisible = { display: visible ? 'none' : '' }
  const showWhenVisible = { display: visible ? '' : 'none' }

  const toggleVisibility = () => {
    setVisible(!visible)
  }


  useImperativeHandle(refs, () => {
    return {
      toggleVisibility
    }
  })

  return (
    <div>
      <div style={hideWhenVisible}>
        
        <Button className="m-3" variant="light" onClick={toggleVisibility}>
          <Image className="m-2" style={{ width: 20 }} src="/downarrow.png" />
          {props.buttonLabel}
        </Button>

      </div>
      <div style={showWhenVisible} className='togglableContent'>
        {props.children}
        <Button className="m-3" variant="light" onClick={toggleVisibility}>
          <Image className="m-2" style={{ width: 20 }} src="/uparrow.png" />
          Hide
        </Button>
      </div>
    </div>
  )
})

Togglable.displayName = 'Togglable'

export default Togglable