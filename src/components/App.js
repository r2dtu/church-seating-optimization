import React, { useState, useRef } from 'react';
import { CSSTransition, TransitionGroup } from 'react-transition-group';

import { Formik } from 'formik';

import Alert from 'react-bootstrap/Alert';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import InputForm from './InputForm';
import TableView from './TableView';

import { validationSchema, initialValues } from '../utils/validation';
import { replaceErrors } from '../utils/error';
import { location } from '../utils/spreadsheet';

// Taken from this lovely post: https://blog.logrocket.com/programmatic-file-downloads-in-the-browser-9a5186298d5c/
const downloadBlob = (blob, filename) => {
  // Create an object URL for the blob object
  const url = URL.createObjectURL(blob);

  // Create a new anchor element
  const a = document.createElement('a');

  // Set the href and download attributes for the anchor element
  // You can optionally set other attributes like `title`, etc
  // Especially, if the anchor element will be attached to the DOM
  a.href = url;
  a.download = filename || 'download';

  // Click handler that releases the object URL after the element has been clicked
  // This is required for one-off downloads of the blob content
  const clickHandler = () => {
    setTimeout(() => {
      URL.revokeObjectURL(url);
      a.removeEventListener('click', clickHandler);
    }, 150);
  };

  // Add the click event listener on the anchor element
  // Comment out this line if you don't want a one-off download of the blob content
  a.addEventListener('click', clickHandler, false);

  // Programmatically trigger a click on the anchor element
  // Useful if you want the download to happen automatically
  // Without attaching the anchor element to the DOM
  // Comment out this line if you don't want an automatic download of the blob content
  a.click();
};

const InputErrorText = ({ error }) => {
  const [at, loc] = location(error.row, error.col);
  console.log(error);
  return (
    <div>
      <div>In file <strong>"{error.file}"</strong>{at}{loc && <strong>{loc}</strong>}: {error.description}</div>
      {(error.row !== -1 && error.col !== -1) && <TableView className="ml-2 mt-2" {...error} />}
    </div>
  );
};

function App() {
  const [fatalError, setFatalError] = useState({});
  const [inputError, setInputError] = useState({});
  const [exception, setException] = useState('');
  const [success, setSuccess] = useState(false);

  const bottomRef = useRef(null);

  const handleSubmit = async (data, formik) => {
    // Need a helper function to reset files on error, so that users don't try resubmitting with cached page data.
    const resetFiles = (validate = false) => {
      formik.setFieldValue('pewFile', null, validate);
      formik.setFieldValue('familyFile', null, validate);
    };

    // Package the data into a FormData for the request.
    const formData = new FormData();
    for (const key in data) {
      formData.append(key, data[key]);
    }

    // Clear all errors.
    setFatalError({});
    setInputError({});
    setException('');
    setSuccess(false);

    try {
      // Make the request!
      const response = await fetch('/api/upload', {
        method: 'POST',
        mode: 'no-cors',
        cache: 'no-cache',
        body: formData,
      });

      if (response.status === 500) {
        // Fatal server error.
        const error = await response.json();
        setFatalError(error);
        resetFiles(true);
      } else if (response.status === 400) {
        // Bad inputs.
        const error = await response.json();
        setInputError(error);
        resetFiles(true);
      } else if (!response.ok) {
        // Something else went wrong...
        setException(await response.text());
        resetFiles(true);
      } else {
        // Trigger download from the response.
        setSuccess(true);
        setTimeout(() => {
          setSuccess(false);
        }, 6000);
        const blob = await response.blob();
        downloadBlob(blob, 'seating_arrangements.csv');
        formik.resetForm();
        resetFiles();
      }

      bottomRef.current.scrollIntoView({ block: 'end', behavior: 'smooth' });
    } catch (err) {
      // Super fatal error happened, like a network timeout.
      setException(JSON.stringify(err, replaceErrors));
    }
  };

  return (
    <Container className="py-4" ref={bottomRef}>
      <h1>Church Seating Optimization Program</h1>
      <Row className="mb-3">
        <Col>
          <Formik
            validationSchema={validationSchema}
            onSubmit={handleSubmit}
            initialValues={initialValues}>
            {InputForm}
          </Formik>
        </Col>
      </Row>
      <TransitionGroup>
        {fatalError.description && <CSSTransition
          key="fatalError"
          classNames="alert"
          timeout={500}>
          <Row>
            <Col>
              <Alert variant="danger">
                <div>{fatalError.description}</div>
                <br />
                <div>
                  Trace: <pre>{fatalError.trace}</pre>
                </div>
                <div>
                  Inputs: <pre>{JSON.stringify(fatalError.inputs, null, 2)}</pre>
                </div>
              </Alert>
            </Col>
          </Row>
        </CSSTransition>}
        {inputError.errors && <CSSTransition
          key="inputError"
          classNames="alert"
          timeout={500}>
          <Row>
            <Col>
              <Alert variant="warning">
                <div>{inputError.description}</div>
                {inputError.errors.map((error, i) => <InputErrorText key={i} error={error} />)}
              </Alert>
            </Col>
          </Row>
        </CSSTransition>}
        {exception && <CSSTransition
          key="exception"
          classNames="alert"
          timeout={500}>
          <Row>
            <Col>
              <Alert variant="danger">
                <div>Yikes! Something unexpected happened, either with your network or with the seat assignments service. Please try again.</div>
                <br />
                <div>If this issue persists, forward the details below to a developer:</div>
                <pre>{exception}</pre>
              </Alert>
            </Col>
          </Row>
        </CSSTransition>}
        {success && <CSSTransition
          key="success"
          classNames="alert"
          timeout={500}>
          <Row>
            <Col>
              <Alert variant="success">Success!</Alert>
            </Col>
          </Row>
        </CSSTransition>}
      </TransitionGroup>
    </Container>
  );
}

export default App;
