import {View,Text,Button,TextInput,StyleSheet,FlatList} from 'react-native';
import { useState,useRef, useEffect } from "react";
import {
  useChatInteract,
  useChatMessages,
  IStep
} from "../../libs/cl-sdk-1.2";

const Separator = () => <View style={styles.separator}/>;

const Playground = () => {
  const [inputValue, setInputValue] = useState<string>("");

  const { sendMessage } = useChatInteract();
  const { messages } = useChatMessages();

  const handleSendMessage = () => {
    const content = inputValue.trim();
    if(content){
      const message = {
        name: "user",
        type: "user_message" as const,
        output: content,
      };
      sendMessage(message,[]);
      setInputValue("");
    }
  };

  const renderMessage = (message:IStep) => {
    return (
      <View
        key={message.id}
        style={styles.item}
      >
        <Text style={styles.title}>
          {message.type}
        </Text>
        <Text style={styles.content}>
          {message.output}
        </Text>
        <Text style={styles.footer}>
          {new Date(message.createdAt).toLocaleString()}
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={messages}
        renderItem={({item:message}) => renderMessage(message)}
        keyExtractor={item => item.id}
      />
      <Separator/>
      <View
        style={{margin:10}}
      >
        <TextInput
          style={styles.input}
          onChangeText={setInputValue}
          value={inputValue}
        />
        <Button
          onPress={handleSendMessage}
          title={"Send Message"}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    width:"100%"
  },
  input: {
    height: 40,
    marginBottom: 10,
    padding:5,
    borderWidth: 1,
    borderColor:'#999999',
    borderRadius:3
  },
  separator: {
    marginVertical: 5,
    borderBottomColor: '#999999',
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  item: {
    display:"flex",
    flexGrow:1,
    backgroundColor: 'rgba(170, 170, 170, 0.15)',
    borderRadius: 10,
    padding: 10,
    margin:10,
  },
  title: {
    fontSize: 16,
    color:"#666666",
  },
  content: {
    marginVertical:10,
  },
  footer: {
    fontSize: 8,
    color: "#999999"
  }
});

export {Playground};