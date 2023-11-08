Title : Agent Playground Base
Tags : [playground]

# Agent Prompt Playground

The Prompt Playground is a unique feature that allows developers to visualize, iterate, and version prompts, thereby enhancing the development/debugging process.

More info and a video here: https://docs.chainlit.io/concepts/prompt-playground/overview

## Example Usage

To leverage the prompt playground feature in this repository, follow these steps:

1. Import the necessary modules in your application:

   ```python
   from openai import AsyncOpenAI
   import chainlit as cl
   from chainlit.prompt import Prompt, PromptMessage
   from chainlit.playground.providers import ChatOpenAI
   ```

2. Set up the necessary variables for your prompt:

   ```python
   client = AsyncOpenAI()

   template = "Hello, {name}!"
   inputs = {"name": "John"}
   settings = {
       "model": "gpt-3.5-turbo",
       "temperature": 0,
       # ... more settings
   }
   ```

3. Create the Chainlit Prompt instance:

   ```python
   prompt = Prompt(
       provider=ChatOpenAI.id,
       inputs=inputs,
       settings=settings,
       messages=[
           PromptMessage(
               template=template,
               formatted=template.format(**inputs),
               role="assistant"
           )
       ]
   )
   ```

4. Make the call to OpenAI and retrieve the completion:

   ```python
   response = await client.chat.completions.create(
       messages=[m.to_openai() for m in prompt.messages], **settings
   )
   prompt.completion = response.choices[0].message.content
   ```

5. Send the message using Chainlit:

   ```python
   await cl.Message(
       content="The content of the message is not important.",
       prompt=prompt,
   ).send()
   ```

6. Run your application and interact with the prompt using the provided template.

That's it! You can now leverage the prompt playground feature in your application using the code from this repository.
