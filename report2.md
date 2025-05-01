# TASK 2.1 – Prompt Structure Experimentation (Cohere)

## Prompt Format 1: Standard Text-Based

Example:
"Manual excerpt:\n
...\n
DEFUSER sees or asks:\n
...\n"

Result:
Moderate accuracy. Reasonable for casual interaction, but lack of structure sometimes caused the model to get confused about what task it was supposed to complete.

But sometimes the model produced:
<|im_start|>assistant
Here's how the module works:
1 The user is presented with a sequence of flashing colors.
2 The user presses the buttons to repeat the sequence.
3 The sequence is presented again, and the user asks if they want

This suggests the model fell back into generic instruction behavior, likely due to ambiguity in the input format.

---

## Prompt Format 2: Structured Markdown

Example:
"### Manual
\n...
\n### DEFUSER sees or asks
\n..."

Result:
Slightly higher accuracy. Markdown-style sectioning helped the model separate sections from each other, leading to a clearer understanding of what to focus on. The model produced shorter, more direct responses.

---

## Prompt Format 3: JSON-Formatted

Example (simplified structure):  
{ "role": "Expert", "input": ..., "output": ... }

Result:
This basic structure didn’t affect results in any significant way. Implementing a more detailed JSON-style prompt like:

{
  "role": "Expert",
  "manual": "...",
  "bomb_state": {
    "wires": [...],
    "serial_number": "PAABB4"
  },
  "task": "Which wire should be cut?"
}

was not practical with the current testing setup.
