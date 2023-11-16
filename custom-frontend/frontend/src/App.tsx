import { useEffect } from "react";

import { useChatSession } from "@chainlit/react-client";
import { Playground } from "./components/playground";

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
        <Playground />
      </div>
    </>
  );
}

export default App;
