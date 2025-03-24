## Extended Thinking Cookbook

Using Chainlit’s native `@step` decorator and a bit of custom JavaScript, it's easy to recreate the "extended thinking" effect we see in many popular LLM applications such as those by Anthropic, OpenAI, Meta, or DeepSeek.

For this cookbook example, I wanted the application to leverage native thinking tokens exposed at the API level to developers. Unfortunately, OpenAI and Meta do not provide access to raw thinking tokens. As a result, when using models from those companies, Chain-of-Thought reasoning is typically achieved by prompting external models (like GPT-4o) to break problems down and then delegating sub-questions to other models.

In contrast, this application uses Anthropic’s Claude 3.7 Sonnet. Anthropic is one of the few companies that expose a model's internal thinking via their API. This makes Claude an excellent choice for showcasing the difference between “Extended Thinking” (i.e., thinking tokens) and simply streaming a final response to the screen.

Additionally, I modified the logic for the thinking step dropdown so that it automatically opens for each message. You can still close it manually if you'd like to keep the chat history cleaner.

---

### How to Use

1. Clone this cookbook example.

2. Navigate into the cloned directory:

   ```bash
   cd <cloned-directory>
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Rename the `.env.example` file to `.env`, and add your `ANTHROPIC_API_KEY`.

5. Run the app:

   ```bash
   chainlit run app.py
   ```

6. After running the app for the first time, a `.chainlit` folder will be automatically created with a `config.toml` file inside it.  
   Delete that auto-generated file and replace it by copying the `config.toml` file from the main directory of this example application into the `.chainlit` folder.  
   This will apply the custom JavaScript and CSS settings I’ve included.

7. Run the app again:

   ```bash
   chainlit run app.py
   ```

8. Once the application opens, type any question into the chat input box.  
   The model will decide—based on the complexity of your question—whether to go through a short or extended thinking step. After that, it will stream the final response separately to the screen.

The model supports message history, so feel free to engage in a natural back-and-forth and use it just like your own personal LLM-powered application.
