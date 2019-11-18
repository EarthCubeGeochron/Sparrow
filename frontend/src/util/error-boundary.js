import React from 'react'
import {Callout} from '@blueprintjs/core'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null};
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { error };
  }

  componentDidCatch(error, info) {
    // You can also log the error to an error reporting service
    console.log(error);
  }

  render() {

    if (this.state.error != null) {
      let {description} = this.props;
      const {error} = this.state;
      if (description == null) description = error.toString();
      // You can render any custom fallback UI
      return <Callout title={"A rendering error occurred"} icon='error' intent='danger'>
        <p>{description}</p>
      </Callout>;
    }

    return this.props.children;
  }
}

export {ErrorBoundary}
