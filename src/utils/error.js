// Helper function for serializing Error objects in JSON.stringify(). https://stackoverflow.com/a/18391400/2655566
export const replaceErrors = (_, value) => {
  if (value instanceof Error) {
    const error = {};
    for (const key of Object.getOwnPropertyNames(value)) {
      error[key] = value[key];
    }
    return error;
  }

  return value;
};
