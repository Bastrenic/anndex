import { createGlobalStyle } from 'styled-components';
import { BrowserRouter } from 'react-router-dom';
import { Fragment } from 'react';
import Router from './Router';

export const API_URL = 'http://localhost:8000';

const GlobalStyle = createGlobalStyle`
  html, body {
    margin: 0;
    padding: 0;
    height: 100%;
  }
`

function App() {
  return (
    <Fragment>
      <GlobalStyle/>
      <BrowserRouter>
        <Router>
        </Router>
      </BrowserRouter>
    </Fragment>
  )
}

export default App
