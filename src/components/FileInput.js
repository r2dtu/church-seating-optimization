import React, { useRef, useEffect } from 'react';

import Form from 'react-bootstrap/Form';

const ControlledFileInput = ({ value, ...rest }) => {
  const ref = useRef(null);

  useEffect(() => {
    if (!value) {
      ref.current.value = null;
    }
  }, [value]);

  return <input {...rest} ref={ref} type="file" />;
};


const FileInput = ({ label, placeholder, explanation, field, form, meta, ...props }) => {
  return (
    <>
      <Form.Label>{label}</Form.Label>
      <Form.File
        label={field.value?.name || placeholder}
        custom
        value={field.value}
        inputAs={ControlledFileInput}
        feedback={meta.error}
        name={field.name}
        onBlur={field.onBlur}
        onChange={(event) => {
          const file = event.currentTarget.files[0] || null;
          form.setFieldValue(field.name, file);
        }}
        {...props}
      />
      {explanation ? <Form.Text className="text-muted">{explanation}</Form.Text> : null}
    </>
  );
};

export default FileInput;