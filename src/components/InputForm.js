import React from 'react';

import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { Field } from 'formik';

import NumberInput from './NumberInput';
import FileInput from './FileInput';

const InputForm = (formik) => {
  const {
    handleSubmit,
    touched,
    errors,
  } = formik;

  return (
    <Form noValidate onSubmit={handleSubmit}>
      <Form.Group>
        <NumberInput
          name="maxCapacity"
          label="Maximum Capacity"
          placeholder="e.g. 100"
          isInvalid={touched.maxCapacity && !!errors.maxCapacity}
          explanation="This number represents the TOTAL number of people allowed in the church."
        />
      </Form.Group>
      <Form.Group>
        <NumberInput
          name="reservedSeating"
          label="Number of Reserved Seating"
          placeholder="e.g. 10"
          isInvalid={touched.reservedSeating && !!errors.reservedSeating}
          explanation="This number represents the number of people to not include in the seating chart, but need space in the church to sit. Do not include the pews you are reserving for them in the pew info CSV file. This number is only used in calculating how many families can potentially be seated."
        />
      </Form.Group>
      <Form.Group>
        <NumberInput
          name="separationRadius"
          label="Separation Radius (in feet)"
          placeholder="e.g. 6"
          isInvalid={touched.separationRadius && !!errors.separationRadius}
          explanation="How far away each group needs to be seated from one another. CoVid-19 social distancing guidelines require at least 6 feet."
        />
      </Form.Group>
      <Form.Group>
        <NumberInput
          name="seatWidth"
          label="Seat Width (in inches)"
          placeholder="e.g. 18"
          isInvalid={touched.seatWidth && !!errors.seatWidth}
          explanation="Width of a seat in inches."
        />
      </Form.Group>
      <Form.Group>
        <Field name="pewFile">
          {(props) => (
            <FileInput
              label="Pew Info CSV File"
              placeholder="No file chosen"
              isInvalid={touched.pewFile && !!errors.pewFile}
              explanation="The CSV file containing information about pew section, rows, and sizes (in number of seats). NOTE: Only include available pews for groups to be seated in this file. Information about reserved pews should not be present in this file."
              {...props}
            />
          )}
        </Field>
      </Form.Group>
      <Form.Group>
        <Field name="familyFile">
          {(props) => (
            <FileInput
              label="Household Info CSV File"
              placeholder="No file chosen"
              isInvalid={touched.familyFile && !!errors.familyFile}
              explanation="The CSV file containing information about household names, contact information, and sizes (in number of people). NOTE: Families with sizes larger than the largest pew size will not be seated! Please break them up into different groups if able."
              {...props}
            />
          )}
        </Field>
      </Form.Group>
      <Button type="submit">Download Seat Assignments</Button>
    </Form>
  );
}

export default InputForm;
