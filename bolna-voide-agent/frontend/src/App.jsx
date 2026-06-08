import { useState } from "react";
import axios from "axios";

function App() {

  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchCustomer = async () => {

    setLoading(true);

    try {

      const response = await axios.get(
        "http://localhost:8000/latest-customer"
      );

      setCustomer(response.data);

    } catch (error) {

      console.log(error);

    }

    setLoading(false);
  };

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Arial"
      }}
    >
      <h1>Bolna Customer Data</h1>

      <button onClick={fetchCustomer}>
        Get Latest Customer
      </button>

      <br />
      <br />

      {loading && <h3>Loading...</h3>}

      {customer && (
        <div>
          <h2>Name: {customer.name}</h2>
          <h2>Age: {customer.age}</h2>
          <h2>Phone: {customer.phone}</h2>
        </div>
      )}
    </div>
  );
}

export default App;