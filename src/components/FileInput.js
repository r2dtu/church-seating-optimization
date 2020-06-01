import React from 'react';

import Form from 'react-bootstrap/Form';

const FileInput = ({ label, placeholder, explanation, field, form, meta, ...props }) => {
  return (
    <>
      <Form.Label>{label}</Form.Label>
      <Form.File
        label={placeholder}
        custom
        feedback={meta.error}
        name={field.name}
        onBlur={field.onBlur}
        onChange={(event) => {
          const file = event.currentTarget.files[0];
          form.setFieldValue(field.name, file);
        }}
        {...props}
      />
      {explanation ? <Form.Text className="text-muted">{explanation}</Form.Text> : null}
    </>
  );
};

export default FileInput;