import { useEffect } from "react";
import "./App.css";
import { useChatSession } from "@chainlit/components";
import MessagePlayground from "./Playground";

const CHAINLIT_SERVER = "http://localhost:8000";
const userEnv = {};

function App() {
  const { connect } = useChatSession();

  useEffect(() => {
    connect({ wsEndpoint: CHAINLIT_SERVER, userEnv });
  }, [connect]);

  return (
    <>
      <div>
        <MessagePlayground />
      </div>
    </>
  );
}

export default App;
