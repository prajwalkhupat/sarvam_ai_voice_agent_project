import axios from "axios";

const API =
"http://localhost:8000";

export const askAI =
async (message) => {

  const response =
  await axios.post(
    `${API}/chat`,
    {
      message
    }
  );

  return response.data;
};