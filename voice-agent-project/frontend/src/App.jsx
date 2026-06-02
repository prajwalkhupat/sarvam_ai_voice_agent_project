import { useState } from "react";
import { askAI } from "./api";

function App() {

  const [listening,
  setListening] =
  useState(false);

  const [userText,
  setUserText] =
  useState("");

  const [aiResponse,
  setAiResponse] =
  useState("");

  const startVoice =
  () => {

    const SpeechRecognition =
      window
      .SpeechRecognition ||

      window
      .webkitSpeechRecognition;

    const recognition =
      new SpeechRecognition();

    recognition.lang =
      "en-US";

    recognition.start();

    setListening(true);

    recognition.onresult =
    async (event) => {

      const text =
      event.results[0][0]
      .transcript;

      setUserText(text);

      const result =
      await askAI(text);

      setAiResponse(
        result.ai_response
      );

      speak(
        result.ai_response
      );

      setListening(false);
    };
  };

  const speak =
  (text) => {

    const speech =
    new SpeechSynthesisUtterance(
      text
    );

    speech.rate = 1;

    window
    .speechSynthesis
    .speak(speech);
  };

  return (
    <div
      style={{
        padding: "50px",
        textAlign:
        "center"
      }}
    >
      <h1>
        AI Voice Agent
      </h1>

      <button
        onClick={
          startVoice
        }
        style={{
          padding:
          "15px 30px",
          fontSize:
          "18px"
        }}
      >
        {
          listening
          ? "Listening..."
          : "Start Voice"
        }
      </button>

      <div
        style={{
          marginTop: 40
        }}
      >
        <h3>
          You Said:
        </h3>

        <p>
          {userText}
        </p>

        <h3>
          AI Response:
        </h3>

        <p>
          {aiResponse}
        </p>
      </div>
    </div>
  );
}

export default App;