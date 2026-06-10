import { useState } from "react";
import axios from "axios";

function App() {
  const [numbers, setNumbers] = useState("");
  const [results, setResults] = useState([]);

  const startCampaign = async () => {
    const phoneNumbers = numbers
      .split("\n")
      .map((n) => n.trim())
      .filter(Boolean);

    await axios.post(
      "http://localhost:8000/start-campaign",
      {
        numbers: phoneNumbers,
      }
    );

    alert("Campaign Started");
  };

  const loadResults = async () => {
    const response = await axios.get(
      "http://localhost:8000/campaign-results"
    );

    setResults(response.data.results);
  };

  return (
    <div style={{ padding: 30 }}>
      <h1>Bolna Campaign Manager</h1>

      <textarea
        rows={10}
        cols={40}
        placeholder="Enter phone numbers"
        value={numbers}
        onChange={(e) =>
          setNumbers(e.target.value)
        }
      />

      <br />
      <br />

      <button onClick={startCampaign}>
        Start Campaign
      </button>

      <button
        onClick={loadResults}
        style={{ marginLeft: 20 }}
      >
        Refresh Results
      </button>

      <hr />

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Phone</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {results.map((row, index) => (
            <tr key={index}>
              <td>{row.name}</td>
              <td>{row.age}</td>
              <td>{row.phone}</td>
              <td>{row.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;