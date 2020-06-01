import React from 'react';

import { useField } from 'formik';

import Form from 'react-bootstrap/Form';

const NumberInput = ({ label, placeholder, explanation, ...props }) => {
  const [field, meta] = useField(props);

  return (
    <>
      <Form.Label>{label}</Form.Label>
      <Form.Control
        type="number"
        placeholder={placeholder}
        {...field}
        {...props}
      />
      <Form.Control.Feedback type="invalid">{meta.error}</Form.Control.Feedback>
      {explanation ? <Form.Text className="text-muted">{explanation}</Form.Text> : null}
    </>
  );
};

export default NumberInput;