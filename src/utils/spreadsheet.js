// Yet another lovely stackoverflow answer: https://stackoverflow.com/a/8241071/2655566
export const columnNameForNum = (n) => {
  const ordA = 'A'.charCodeAt(0);
  const ordZ = 'Z'.charCodeAt(0);
  const len = ordZ - ordA + 1;

  n -= 1; // This algo is 0-indexed, so have to convert 1-indexing to 0-indexing.

  var s = "";
  while (n >= 0) {
    s = String.fromCharCode(n % len + ordA) + s;
    n = Math.floor(n / len) - 1;
  }
  return s;
};

export const cell = (row, col) => columnNameForNum(col) + row;

/**
 * Returns the "location" of a (row, col) pair.
 * The location is a tuple of a prepsoitional phrase, paired with the
 * actual number or cell that represents the (row, col) pair.
 */
export const location = (row, col) => {
  if (col === -1 && row === -1) {
    return ['', ''];
  }

  if (col === -1) {
    return [' at row ', row];
  }
  
  if (row === -1) {
    return [' at column ', col];
  }

  return [' at cell ', cell(row, col)];
}