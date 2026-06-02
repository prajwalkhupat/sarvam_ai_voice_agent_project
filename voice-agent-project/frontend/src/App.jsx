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

  const startVoice = () => {

    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

      alert(
        "Speech Recognition not supported"
      );

      return;
    }

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

        try {

          const result =
            await askAI(text);

          console.log(
            "API Response:",
            result
          );

          if (
            result.success
          ) {

            setAiResponse(
              result.ai_response
            );

            speak(
              result.ai_response
            );

          } else {

            setAiResponse(
              result.error
            );
          }

        } catch (error) {

          console.error(
            error
          );

          setAiResponse(
            "Backend connection failed"
          );
        }

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
        maxWidth:
          "800px",
        margin:
          "40px auto",
        textAlign:
          "center"
      }}
    >

      <h1>
        Sarvam AI Voice Agent
      </h1>

      <button
        onClick={
          startVoice
        }
      >
        {
          listening
            ? "Listening..."
            : "Start Voice"
        }
      </button>

      <hr />

      <h3>
        You Said
      </h3>

      <p>
        {userText}
      </p>

      <h3>
        AI Response
      </h3>

      <p>
        {aiResponse}
      </p>

    </div>
  );
}

export default App;