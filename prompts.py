GENERATE_QUESTION_PROMPT = """You will generate 2 Turkish questions for a given text content.

Text:
```
{text}
```

Only output in the following json format:
```json
[
  "question1",
  "question2"
]
```

Make sure the questions are not too specific to the text.
These questions should be for learning some topic or information, not specific answers or information.
Like: "DPO nasıl çalışır", "Işığın yansıması nasıl oluşur?", "Matematikte fonksiyonlar nasıl çalışır?", "Kalp krizi nasıl önlenir?"...

Make sure the questions are not too similar to each other.
Make sure the questions are not too long.
Make sure the questions are in Turkish and they are not too long."""




GENERATE_ANSWER_PROMPT = """You are a highly skilled and experienced teacher.

TASK: Answer the following question in a detailed, understandable and engaging way in Turkish.

QUESTION/TOPIC:
```
{question}
```

FORMAT REQUIREMENTS:
1. Wrap your entire response in ```md and ``` tags
2. Use markdown formatting (headings, lists, tables, bold, italic, etc.)
3. Create structured, readable content
4. Jump directly into the content - no greetings
5. Provide long, detailed, and in-depth explanations

AVAILABLE INTERACTIVE COMPONENTS:

Mermaid Diagram Example:
```mermaid
# ALWAYS put the block contents inside "" (double quotes) as it can lead to syntax errors
flowchart TD
    A["Başlangıç"] --> B["Süreç 1"]
    A --> C["Süreç 2"]
    B --> D["Sonuç"]
    C --> D
```

Matplotlib Graph Example:
```python.matplotlib
import matplotlib.pyplot as plt
import numpy as np
# Example code
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('Sine Function')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.show()
```

AI Generated Image Example:
```image
Generate a textbook style image/illustration of:

[prompt here]

Light beige background color.
There should not be any text in the image.
```

COMPONENT USAGE GUIDELINES:
- ALWAYS put the block contents inside "" (double quotes) in mermaid as it requires it
- Use the ```python.matplotlib ``` syntax to use the matplotlib graph component
- Use the ```mermaid ``` syntax to use the mermaid diagram component
- Use the ```image ``` syntax to prompt an image generator AI to generate an image/illustration
- Use interactive components strategically to enhance learning
- Make sure to write `plt.show()` at the end of the code block to show the graph so that it can be rendered inline
- All components render automatically inline
- Use backticks for inline math: `f(x) = y`
- Choose components that best illustrate your topic, you dont have to pick only one component, you can pick multiple components
- Do NOT ever indent the code blocks, it will break the rendering, but you can indent the code blocks inside the code blocks

CONTENT REQUIREMENTS:
- Write entirely in Turkish
- Provide comprehensive, educational explanations
- Use engaging, teacher-like tone without being cringy
- Structure content logically with clear sections
- Include examples and practical applications where relevant
- Avoid using cringe phrasing or emojis, keep it entertaining and engaging while not being too cringy
- Make sure that the formats you are using exactly match the templates I provided
- Explain the graph or diagram before you rite the code for it so the person can understand it easily
- Make sure you only change the [prompt here] part when generating an image/illustration
- You can remove the "Light beige background color." part from the image generation prompt if the image should not have a background color

Now answer the question/topic. Write your Turkish response between ```md and ``` tags."""
