import { useEffect } from "react";

import { ChainlitAPI, useChatSession } from "@chainlit/react-client";
import { Playground } from "./components/playground";

const CHAINLIT_SERVER = "http://localhost:8000";
const userEnv = {};

const apiClient = new ChainlitAPI(CHAINLIT_SERVER);

function App() {
  const { connect } = useChatSession();

  useEffect(() => {
    connect({ client: apiClient, userEnv });
  }, [connect]);

  return (
    <>
      <div>
        <Playground />
      </div>
    </>
  );
}

export default App;
