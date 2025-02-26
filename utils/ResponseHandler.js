const handleResponse = (res, data, message) => {
    res.status(200).json({ success: true, message, data });
  };
  
  const handleError = (res, error) => {
    console.error(error);
    const errorMessage =
      error instanceof Error ? error.message : 'Internal Server Error';
    res.status(500).json({ success: false, error: errorMessage });
  };
  
  module.exports = { handleResponse, handleError };
  