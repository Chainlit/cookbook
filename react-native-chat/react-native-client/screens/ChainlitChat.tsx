import {View,Text, Button} from 'react-native';
import { useEffect } from 'react'
import { Playground } from '../components/playground';
import { useRecoilValue } from "recoil";
import { sessionState, useChatSession } from "../libs/cl-sdk-1.2";
import { CHAINLIT_SERVER_HOST } from '../chainlit.config';

const userEnv = {};


const ChainlitChat = () => {
  const { connect } = useChatSession();
  const session = useRecoilValue(sessionState);
  useEffect(()=>{
    if (session?.socket.connected) {
      return;
    }
    fetch(`${CHAINLIT_SERVER_HOST}/custom-auth`)
      .then((res) => {
        return res.json();
      })
      .then((data) => {
        connect({
          userEnv,
          accessToken: `Bearer: ${data.token}`,
        });
      });
  },[connect]);
  return (
    <Playground/>
  );
}

export default ChainlitChat;

