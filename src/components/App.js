import React, { useEffect } from 'react';

import { Formik } from 'formik';
import * as yup from 'yup';

import Container from 'react-bootstrap/Container';
import bsCustomFileInput from 'bs-custom-file-input';

import InputForm from './InputForm';

const isCsvType = (value) => {
  return value && value.type === 'text/csv';
}
const schema = yup.object({
  maxCapacity: yup.number().min(1, 'Must have at least one spot of capacity.').required('A maximum capacity is required.'),
  reservedSeating: yup.number().min(0, 'Cannot have a negative number of seats.').max(yup.ref('maxCapacity'), 'Reserved seating cannot exceed maximum capacity.').required('Reserved seating is required.'),
  separationRadius: yup.number().required('A separation radius is required.'),
  seatWidth: yup.number().required('A seat width is required.'),
  pewFile: yup.mixed().required('A pew file is required.').test('fileFormat', 'Must be a CSV file.', isCsvType),
  familyFile: yup.mixed().required('A household file is required.').test('fileFormat', 'Must be a CSV file.', isCsvType),
});

const initialValues = {
  maxCapacity: '',
  reservedSeating: '',
  separationRadius: '',
  seatWidth: '',
  pewFile: '',
  familyFile: '',
};

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

function App() {
  useEffect(() => {
    // Set up custom bootstrap file inputs (ones that display the filename when selected).
    bsCustomFileInput.init();
  }, []);

  const handleSubmit = async (data) => {
    // Package the data into a FormData for the request.
    const formData = new FormData();
    for (const key in data) {
      formData.append(key, data[key]);
    }

    // Make the request!
    const blob = await fetch('/api/upload', {
      method: 'POST',
      mode: 'no-cors',
      cache: 'no-cache',
      body: formData,
    }).then(response => response.blob());

    // Trigger download from the response.
    downloadBlob(blob, 'seating_arrangements.csv');
  };

  return (
    <Container className="py-4">
      <h1>Church Seating Optimization Program</h1>
      <Formik validationSchema={schema} onSubmit={handleSubmit} initialValues={initialValues}>
        {InputForm}
      </Formik>
    </Container>
  );
}

export default App;
