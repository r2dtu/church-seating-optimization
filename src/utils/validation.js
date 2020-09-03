import * as yup from 'yup';

// text/csv is normal
// the other garbage is for Windows
const isCsvType = (value) => {
  return value && (value.type === 'text/csv' || value.type === 'application/vnd.ms-excel');
}

export const validationSchema = yup.object({
  maxCapacity: yup.number().min(1, 'Must have at least one spot of capacity.').required('A maximum capacity is required.'),
  reservedSeating: yup.number().min(0, 'Cannot have a negative number of seats.').max(yup.ref('maxCapacity'), 'Reserved seating cannot exceed maximum capacity.').required('Reserved seating is required.'),
  separationRadius: yup.number().required('A separation radius is required.'),
  seatWidth: yup.number().min(1, 'Seats must have a positive non-zero width.').required('A seat width is required.'),
  pewFile: yup.mixed().required('A pew file is required.').test('fileFormat', 'Must be a CSV file.', isCsvType),
  familyFile: yup.mixed().required('A household file is required.').test('fileFormat', 'Must be a CSV file.', isCsvType),
});

export const initialValues = {
  maxCapacity: '',
  reservedSeating: '',
  separationRadius: '',
  seatWidth: '',
  pewFile: null,
  familyFile: null,
};
