import React, { useState } from "react";
import {
  Container,
  Paper,
  Box,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
} from "@mui/material";
import { useChatMessages, useChatInteract } from "@chainlit/components";
import { v4 as uuidv4 } from "uuid";

const MessagePlayground = () => {
  const [inputValue, setInputValue] = useState("");

  const { sendMessage } = useChatInteract();
  const { messages } = useChatMessages();

  console.log("messages", messages);

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      const message = {
        id: uuidv4(),
        author: "user",
        content: inputValue,
        authorIsUser: true,
        createdAt: new Date().toISOString(),
      };
      sendMessage(message, []);
      setInputValue("");
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3} sx={{ mt: 4, p: 2 }}>
        <Box sx={{ mb: 2 }}>
          <List>
            {messages.map((message, index) => (
              <React.Fragment key={message.id}>
                <ListItem alignItems="flex-start">
                  <ListItemText
                    primary={message.author}
                    secondary={message.content}
                    primaryTypographyProps={{
                      color: message.authorIsUser
                        ? "primary.main"
                        : "text.primary",
                      fontWeight: "bold",
                    }}
                  />
                </ListItem>
                {index < messages.length - 1 && (
                  <Divider variant="inset" component="li" />
                )}
              </React.Fragment>
            ))}
          </List>
        </Box>
        <Box
          component="form"
          sx={{
            display: "flex",
            alignItems: "center",
            "& > :not(style)": { m: 1 },
          }}
          noValidate
          autoComplete="off"
        >
          <TextField
            fullWidth
            label="Type your message"
            variant="outlined"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                handleSendMessage();
              }
            }}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSendMessage}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default MessagePlayground;
