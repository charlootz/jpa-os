# Use prompt templates and variables - Claude Docs

Prompt engineering

Use prompt templates

Copy page

When deploying an LLM-based application with Claude, your API calls will typically consist of two types of content:

- **Fixed content:** Static instructions or context that remain constant across multiple interactions
- **Variable content:**Dynamic elements that change with each request or conversation, such as:
  - User inputs
  - Retrieved content for Retrieval-Augmented Generation (RAG)
  - Conversation context such as user account history
  - System-generated data such as tool use results fed in from other independent calls to Claude

A **prompt template** combines these fixed and variable parts, using placeholders for the dynamic content. In the [Claude Console](https://platform.claude.com/), these placeholders are denoted with **{{double brackets}}**, making them easily identifiable and allowing for quick testing of different values.

* * *

# When to use prompt templates and variables

You should always use prompt templates and variables when you expect any part of your prompt to be repeated in another call to Claude (only via the API or the [Claude Console](https://platform.claude.com/). [claude.ai](https://claude.ai/) currently does not support prompt templates or variables).

Prompt templates offer several benefits:

- **Consistency:** Ensure a consistent structure for your prompts across multiple interactions
- **Efficiency:** Easily swap out variable content without rewriting the entire prompt
- **Testability:** Quickly test different inputs and edge cases by changing only the variable portion
- **Scalability:** Simplify prompt management as your application grows in complexity
- **Version control:** Easily track changes to your prompt structure over time by keeping tabs only on the core part of your prompt, separate from dynamic inputs

The [Claude Console](https://platform.claude.com/) heavily uses prompt templates and variables in order to support features and tooling for all the above, such as with the:

- **[Prompt generator](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompt-generator):** Decides what variables your prompt needs and includes them in the template it outputs
- **[Prompt improver](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompt-improver):** Takes your existing template, including all variables, and maintains them in the improved template it outputs
- **[Evaluation tool](https://platform.claude.com/docs/en/test-and-evaluate/eval-tool):** Allows you to easily test, scale, and track versions of your prompts by separating the variable and fixed portions of your prompt template

* * *

# Example prompt template

Let's consider a simple application that translates English text to Spanish. The translated text would be variable since you would expect this text to change between users or calls to Claude. This translated text could be dynamically retrieved from databases or the user's input.

Thus, for your translation app, you might use this simple prompt template:

```
Translate this text from English to Spanish: {{text}}
```

* * *

## Next steps

[Generate a prompt\\
\\
Learn about the prompt generator in the Claude Console and try your hand at getting Claude to generate a prompt for you.](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompt-generator) [Apply XML tags\\
\\
If you want to level up your prompt variable game, wrap them in XML tags.](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags) [Claude Console\\
\\
Check out the myriad prompt development tools available in the Claude Console.](https://platform.claude.com/)

Ask Docs
![Chat avatar](https://platform.claude.com/docs/images/book-icon-light.svg)

a.claude.ai

# a.claude.ai is blocked

**a.claude.ai** refused to connect.

ERR\_BLOCKED\_BY\_RESPONSE

**a.claude.ai** refused to connect.

![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)