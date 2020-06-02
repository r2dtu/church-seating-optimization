import React from 'react';

import { columnNameForNum } from '../utils/spreadsheet';

const TableView = ({ className, row, col, text }) => {
  const cell = text.trim().split(',')[col - 1];
  col = columnNameForNum(col);

  return (<table className={`${className} table-view`}>
    <tbody>
      <tr>
        <td></td>
        <td></td>
        <td className="err-col">{col}</td>
        <td></td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td className="err-col text-center">⋮</td>
        <td></td>
      </tr>
      <tr>
        <td className="err-row">{row}</td>
        <td className="err-row text-center">⋯</td>
        <td className="err-row err-col">{cell}</td>
        <td className="err-row text-center">⋯</td>
      </tr>
      <tr>
        <td></td>
        <td></td>
        <td className="err-col text-center">⋮</td>
        <td></td>
      </tr>
    </tbody>
  </table>);
};

export default TableView;