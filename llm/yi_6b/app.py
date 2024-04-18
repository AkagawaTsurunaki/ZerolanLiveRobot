from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = '<your-model-path>'

TOKENIZER = AutoTokenizer.from_pretrained(model_path, use_fast=False)

# Since transformers 4.35.0, the GPT-Q/AWQ model can be loaded using AutoModelForCausalLM.
MODEL = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    torch_dtype='auto'
).eval()

# Prompt content: "hi"
messages = [
    {"role": "user", "content": "hi"}
]

input_ids = TOKENIZER.apply_chat_template(conversation=messages, tokenize=True, add_generation_prompt=True, return_tensors='pt')
output_ids = MODEL.generate(input_ids.to('cuda'))
response = TOKENIZER.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)

# Model response: "Hello! How can I assist you today?"
print(response)